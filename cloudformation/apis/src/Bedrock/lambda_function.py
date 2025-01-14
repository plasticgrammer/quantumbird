import json
import os
import boto3
import logging
import html
import re
from typing import Dict, Any, List
from botocore.exceptions import ClientError
from decimal import Decimal
from advisor_roles import ADVISOR_ROLES
from common.utils import create_response, handle_lambda_errors, parse_request_body

# ロガーの設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
stage = os.environ.get('STAGE', 'dev')
members_table_name = f'{stage}-Members'
members_table = dynamodb.Table(members_table_name)

# Bedrockクライアントの初期化
bedrock = boto3.client('bedrock-runtime', region_name = "ap-northeast-1")

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def sanitize_input(text: str) -> str:
    """入力テキストをサニタイズする"""
    if not isinstance(text, str):
        return ""
    
    # HTMLエスケープ
    text = html.escape(text)
    
    # 制御文字の削除（改行とタブは許可）
    text = ''.join(char for char in text if char.isprintable() or char in '\n\t')
    
    # プロンプトインジェクション攻撃のパターンを削除
    # Human: やAssistant: などのプロンプト操作を試みるパターンを削除
    text = re.sub(r'(?i)(Human|Assistant|System):\s*', '', text)
    
    return text

def parse_rating_level(rating: float) -> str:
    """評価レベルを言語化する"""
    if rating >= 4.5:
        return "とても高い"
    elif rating >= 3.5:
        return "高い"
    elif rating >= 2.5:
        return "普通"
    elif rating >= 1.5:
        return "低い"
    else:
        return "とても低い"

def format_projects(projects: list) -> str:
    """プロジェクト情報を整形する"""
    formatted = []
    for project in projects:
        project_name = project.get('name', '')
        work_items = [item.get('content', '') for item in project.get('workItems', [])]
        work_items_str = '\n'.join(f"- {item}" for item in work_items if item)
        if work_items_str:
            formatted.append(f"[{project_name}]\n{work_items_str}")
    
    return '\n\n'.join(formatted) if formatted else "記載なし"

def get_advisor_role_config(role_id: str) -> Dict[str, str]:
    """アドバイザーロールの設定を取得する"""
    if role_id not in ADVISOR_ROLES:
        # デフォルトのロール設定を返す
        return {
            "role": "経験豊富なマネージャー",
            "point": "具体的な行動提案を含め、前向きで実践的なアドバイスを心がけてください。"
        }
    return ADVISOR_ROLES[role_id]

def create_prompt(report: Dict[str, Any], member: Dict[str, Any]) -> str:
    """週次報告の内容からプロンプトを生成する"""

    # クライアントから送られてきたロールIDを使用
    role_id = report.get('advisorRole')
    role_config = get_advisor_role_config(role_id)
    
    adviser_role = sanitize_input(role_config['role'])
    advise_point = sanitize_input(role_config['point'])

    # メンバーの職業と目標を取得
    extra_info = member.get('extraInfo', {})
    occupation = extra_info.get('occupation', '')
    goal = extra_info.get('goal', '')

    # 評価指標の解析
    rating = report.get('rating', {})
    achievement_level = parse_rating_level(rating.get('achievement', 0))
    stress_level = parse_rating_level(rating.get('stress', 0))
    disability_level = parse_rating_level(rating.get('disability', 0))
    # プロジェクト作業の整形
    projects_str = format_projects(report.get('projects', []))
    # 残業時間
    overtime = report.get('overtimeHours', 0)

    adviser_role = sanitize_input(adviser_role)
    advise_point = sanitize_input(advise_point)
    projects_str = sanitize_input(projects_str)
    occupation = sanitize_input(occupation)
    goal = sanitize_input(goal)

    # 付加情報を作成（アドバイザーが付加情報を利用可能＆情報がある場合のみ）
    member_info = ""
    if role_config['useInfo'] and (occupation or goal):
        member_info = "\n【メンバー情報】"
        if occupation:
            member_info += f"\n・職業: {occupation}"
        if goal:
            member_info += f"\n・目標: {goal}"

    # 週次報告内容
    report_content = f"""
【実施した作業】
{projects_str}{member_info}

【振り返り（成果と課題）】
{report.get('issues', '記載なし')}

【改善施策】
{report.get('improvements', '記載なし')}

【各種指標】
・ストレス度: {stress_level} ({rating.get('stress', 0)}/5)
・タスク目標の達成度: {achievement_level} ({rating.get('achievement', 0)}/5)
・タスク遂行の難易度: {disability_level} ({rating.get('disability', 0)}/5)
・残業時間: {overtime}時間/週"""

    # プロンプト
    prompt = f"""Human: あなたは{adviser_role}です。
週次報告へのアドバイスを提供してください。
アドバイスは重要度の高いポイントに絞って、最大500文字程度としてください。
以下が報告の内容です：
{report_content}

{advise_point}
Assistant:"""

    return prompt

def create_summary_prompt(reports: List[Dict[str, Any]]) -> str:
    """週次報告のリストからサマリープロンプトを生成する"""
    all_reports = "\n\n".join([json.dumps(report, ensure_ascii=False) for report in reports])
    
    prompt = f"""Human: あなたはデータアナリストです。
以下の週次報告データを分析し、以下の2点を提供してください：

1. 活動の要点（200文字程度でまとめた1つの文章。文末は「。」で終わる）
2. データから読み取れる重要なインサイト（合計3-5項目）
   - ポジティブな観点（成果、向上点、良好な状態など）：1-3項目
   - 要注意な観点（課題、リスク、改善が必要な点など）：1-3項目

各インサイトには重要度を示すスコア（0-100）を付与してください。
スコアは以下の基準で評価してください：
- 90-100: 即座に対応が必要な重要事項
- 70-89: 近いうちに対応が必要な事項
- 50-69: 継続的な監視が必要な事項
- 0-49: 参考情報として留意する事項

特に以下の点に注目してください：
- 作業内容の傾向
- パフォーマンスとストレスの関係
- 時間管理の状況
- 課題と改善の一貫性

報告データ：
{all_reports}

出力は以下のJSON形式で提供してください：
{{
    "summary": "200文字程度の要約文（文末は「。」で終わる）",
    "insights": {{
        "positive": [
            {{"text": "ポジティブな観点1", "score": 95}},
            {{"text": "ポジティブな観点2", "score": 80}}
        ],
        "negative": [
            {{"text": "要注意な観点1", "score": 90}},
            {{"text": "要注意な観点2", "score": 70}}
        ]
    }}
}}

※インサイトは重要な点のみとし、具体的かつ簡潔に記述してください。
"""
    return prompt

def invoke_claude(prompt: str) -> str:
    """Claude (Anthropic Claude) を呼び出してアドバイスを生成
    温度: 出力のランダム性を制御。低温(0に近い)だと安全で一貫性のある出力が得られるが、単調になることが多い。高温(1以上)だとクリエイティブな応答が期待できる。
    トップP: 確率質量とも呼ばれる。たとえばトップPを0.7と定義した場合には、確率の合計が0.7の中から次の単語が選ばれることになる。
    トップK: 次のトークンを予測する際、全トークンに確率スコアを付与しtop_k数の上位トークンのみを候補として残します。残った候補から、temperature と top_p の影響下で最終選択します。
    """
    try:
        body = json.dumps({
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 600,
            "temperature": 0.8,
            "top_p": 0.9,
            "top_k": 250,
            "anthropic_version": "bedrock-2023-05-31"
        })

        response = bedrock.invoke_model(
            body=body,
            modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
            contentType="application/json",
            accept="application/json"
        )
        
        response_body = json.loads(response.get('body').read())
        logger.info(f"Claude response: {response_body}")
        # Claude 3のレスポンス形式に合わせて変更
        return response_body.get('content')[0].get('text', '')
    
    except ClientError as e:
        logger.error(f"Error invoking Bedrock: {str(e)}")
        raise Exception("アドバイスの生成中にエラーが発生しました。")
    
def check_and_update_advice_tickets(member: Dict[str, Any], member_uuid: str) -> tuple[bool, int]:
    """
    アドバイスチケットの残数をチェックし、利用可能な場合は1枚消費する
    
    Returns:
        tuple[bool, int]: (チケットが利用可能かどうか, 残りチケット数)
    """
    try:
        current_tickets = member.get('adviceTickets', 0)
        
        # チケットが0枚の場合は利用不可
        if current_tickets <= 0:
            return False, current_tickets
            
        # チケットを1枚消費
        response = members_table.update_item(
            Key={'memberUuid': member_uuid},
            UpdateExpression="SET adviceTickets = adviceTickets - :val",
            ExpressionAttributeValues={':val': 1, ':zero': 0},
            ConditionExpression="adviceTickets > :zero",
            ReturnValues="UPDATED_NEW"
        )
        
        # 更新後のチケット数を取得
        remaining_tickets = response.get('Attributes', {}).get('adviceTickets', 0)
        return True, remaining_tickets
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            # 条件チェックに失敗（チケットが0以下）
            return False, 0
        raise e

def handle_summary_request(body: Dict[str, Any]) -> Dict[str, Any]:
    """サマリー生成リクエストを処理"""
    try:
        if 'reports' not in body:
            return create_response(400, {'error': '週次報告のリストが必要です。'})
        
        reports = body['reports']
        if not isinstance(reports, list) or not reports:
            return create_response(400, {'error': '有効な週次報告のリストが必要です。'})
        
        # プロンプトの生成
        prompt = create_summary_prompt(reports)
        
        # Claudeの呼び出し
        claude_response = invoke_claude(prompt)
        
        # JSONレスポンスのパース
        try:
            result = json.loads(claude_response)
            if not isinstance(result, dict) or 'summary' not in result or 'insights' not in result:
                logger.error(f"Invalid Claude response format: {claude_response}")
                result = {
                    'summary': 'サマリーの生成に失敗しました。',
                    'insights': {
                        'positive': ['データの分析に失敗しました。'],
                        'negative': ['データの分析に失敗しました。']
                    }
                }
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding Claude response: {str(e)}")
            result = {
                'summary': 'サマリーの生成に失敗しました。',
                'insights': {
                    'positive': ['データの分析に失敗しました。'],
                    'negative': ['データの分析に失敗しました。']
                }
            }
            
        # 結果の検証とソート処理
        insights = result.get('insights', {})
        if isinstance(insights, dict):
            # positiveインサイトのソート
            if isinstance(insights.get('positive'), list):
                insights['positive'] = sorted(
                    insights['positive'],
                    key=lambda x: float(x.get('score', 0)),
                    reverse=True
                )
            # negativeインサイトのソート
            if isinstance(insights.get('negative'), list):
                insights['negative'] = sorted(
                    insights['negative'],
                    key=lambda x: float(x.get('score', 0)),
                    reverse=True
                )

        # 結果を返す
        return create_response(200, {
            'data': {
                'summary': result.get('summary', ''),
                'insights': insights
            },
            'error': None
        })
        
    except Exception as e:
        logger.error(f"Error processing summary request: {str(e)}")
        return create_response(500, {'error': 'サマリーの生成中にエラーが発生しました。'})

@handle_lambda_errors
def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda関数のメインハンドラー"""
    remaining_tickets = 0
    try:
        body = parse_request_body(event)
        if not body:
            return create_response(400, {'error': 'リクエストボディが必要です。'})
            
        if 'report' in body:
            report_content = body.get('report')
            
            if not report_content:
                return create_response(400, {'error': '週次報告の内容が必要です。'})
                
            member_uuid = report_content.get('memberUuid')
            if not member_uuid:
                return create_response(400, {'error': 'memberUuidが必要です。'})

            # メンバー情報を取得
            response = members_table.get_item(
                Key={'memberUuid': member_uuid}
            )
            member = response.get('Item')
            if not member:
                raise Exception('Member not found')
            
            advisor_role = report_content.get('advisorRole', 'default')  # デフォルト値を設定
            logger.info(f"Execute advice: organization={member.get('organizationId')}, member={member.get('id')}, advisor={advisor_role}")
                        
            # チケットのチェックと消費
            is_available, remaining_tickets = check_and_update_advice_tickets(member, member_uuid)
            if not is_available:
                return create_response(403, {
                    'error': 'アドバイスチケットが不足しています。',
                    'code': 'INSUFFICIENT_TICKETS',
                    'remainingTickets': remaining_tickets
                })
            
            # プロンプトの生成
            prompt = create_prompt(report_content, member)
            
            # Claudeの呼び出し
            claude_response = invoke_claude(prompt)
            formatted_advice = claude_response.strip()

            # 結果を返す
            return create_response(200, {
                'advice': formatted_advice,
                'weekString': report_content.get('weekString'),
                'memberUuid': member_uuid,
                'remainingTickets': remaining_tickets
            })
        
        elif 'reports' in body:
            return handle_summary_request(body)
        
        else:
            return create_response(400, {'error': '無効なリクエストです。'})
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return create_response(500, {
            'error': 'アドバイスの生成中にエラーが発生しました。',
            'remainingTickets': remaining_tickets
        })