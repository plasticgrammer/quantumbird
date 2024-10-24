import json
import os
import boto3
import logging
from typing import Dict, Any
from botocore.exceptions import ClientError
from datetime import datetime

# ロガーの設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Bedrockクライアントの初期化
bedrock = boto3.client('bedrock-runtime', region_name = "ap-northeast-1")

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
            formatted.append(f"【{project_name}】\n{work_items_str}")
    
    return '\n\n'.join(formatted) if formatted else "記載なし"

def create_prompt(report: Dict[str, Any]) -> str:
    """週次報告の内容からプロンプトを生成する"""
    
    # 評価指標の解析
    rating = report.get('rating', {})
    achievement_level = parse_rating_level(rating.get('achievement', 0))
    stress_level = parse_rating_level(rating.get('stress', 0))
    disability_level = parse_rating_level(rating.get('disability', 0))
    # プロジェクト作業の整形
    projects_str = format_projects(report.get('projects', []))
    # 残業時間
    overtime = report.get('overtimeHours', 0)
    
    prompt = f"""Human: あなたは豊富な知識がある優秀なAIメンタルサポーター兼アドバイザーです。
週次報告へのアドバイスを提供してください。以下が報告の内容です：

【実施した作業】
{projects_str}

【振り返り（成果と課題）】
{report.get('issues', '記載なし')}

【改善施策】
{report.get('improvements', '記載なし')}

【各種指標】
・ストレス度: {stress_level} ({rating.get('stress', 0)}/5.0)
・タスク目標の達成度: {achievement_level} ({rating.get('achievement', 0)}/5.0)
・タスク遂行の難易度: {disability_level} ({rating.get('disability', 0)}/5.0)
・残業時間: {overtime}時間

以下の3つの観点から具体的なアドバイスを提供してください：
・業務遂行とワークライフバランス
・メンタルヘルスとストレス管理
・課題解決と改善提案
具体的な行動提案を含め、前向きで実践的なアドバイスを心がけてください。
数値評価を踏まえた具体的な改善アプローチを提案してください。
過剰なアドバイスは避けて、メンタルケアを最重要項目としてください。
Assistant:"""

    return prompt

def invoke_claude(prompt: str) -> str:
    """Claude (Anthropic Claude) を呼び出してアドバイスを生成"""
    try:
        body = json.dumps({
            "prompt": prompt,
            "max_tokens_to_sample": 600,
            "temperature": 0.5,
            "top_p": 1,
            "top_k": 250,
            "stop_sequences": [],
            "anthropic_version": "bedrock-2023-05-31"
        })

        response = bedrock.invoke_model(
            body=body,
            modelId="anthropic.claude-v2:1",
            contentType="application/json",
            accept="application/json"
        )
        
        response_body = json.loads(response.get('body').read())
        # Claude v2のレスポンス形式に合わせて変更
        return response_body.get('completion', '')
    
    except ClientError as e:
        logger.error(f"Error invoking Bedrock: {str(e)}")
        logger.error(f"Request details - ModelId: anthropic.claude-v2, Body: {body}")
        raise Exception("アドバイスの生成中にエラーが発生しました。")

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda関数のメインハンドラー"""
    try:
        logger.info("Received event: %s", json.dumps(event))
        
        # リクエストボディの取得
        if 'body' not in event:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'リクエストボディが必要です。'})
            }
            
        body = json.loads(event['body'])
        report_content = body.get('report')
        
        if not report_content:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': '週次報告の内容が必要です。'})
            }
        
        # プロンプトの生成
        prompt = create_prompt(report_content)
        logger.info(f"Generated prompt: {prompt}")
        
        # Claudeの呼び出し
        claude_response = invoke_claude(prompt)
        logger.info(f"Claude response: {claude_response}")
        
        # 余分な空白行を削除し、改行を適切に保持
        # lines = [line.strip() for line in claude_response.split('\n')]
        # formatted_lines = [line for line in lines if line]
        # formatted_advice = '\n'.join(formatted_lines)
        formatted_advice = claude_response

        # 結果を返す
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'advice': formatted_advice,
                'weekString': report_content.get('weekString'),
                'memberUuid': report_content.get('memberUuid')
            }, ensure_ascii=False)
        }
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'アドバイスの生成中にエラーが発生しました。'
            }, ensure_ascii=False)
        }