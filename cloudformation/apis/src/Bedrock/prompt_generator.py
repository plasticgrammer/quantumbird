import html
import re
import json
from typing import Dict, Any, List
from advisor_roles import ADVISOR_ROLES

def sanitize_input(text: str) -> str:
    """入力テキストをサニタイズする"""
    if not isinstance(text, str):
        return ""
    
    text = html.escape(text)
    text = ''.join(char for char in text if char.isprintable() or char in '\n\t')
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

def get_advisor_role_config(role_id: str) -> Dict[str, str]:
    """アドバイザーロールの設定を取得する"""
    if role_id not in ADVISOR_ROLES:
        return {
            "role": "経験豊富なマネージャー",
            "point": "具体的な行動提案を含め、前向きで実践的なアドバイスを心がけてください。"
        }
    return ADVISOR_ROLES[role_id]

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

def create_prompt(report: Dict[str, Any], member: Dict[str, Any], past_reports: List[Dict[str, Any]] = None) -> str:
    """週次報告の内容からプロンプトを生成する"""
    # レポートから直接アドバイザーロールを取得
    role_id = report.get('advisorRole', 'manager')
    role_config = get_advisor_role_config(role_id)
    
    adviser_role = sanitize_input(role_config['role'])
    advise_point = sanitize_input(role_config['point'])

    extra_info = member.get('extraInfo', {})
    occupation = sanitize_input(extra_info.get('occupation', ''))
    goal = sanitize_input(extra_info.get('goal', ''))

    rating = report.get('rating', {})
    achievement_level = parse_rating_level(rating.get('achievement', 0))
    stress_level = parse_rating_level(rating.get('stress', 0))
    disability_level = parse_rating_level(rating.get('disability', 0))
    projects_str = sanitize_input(format_projects(report.get('projects', [])))
    overtime = report.get('overtimeHours', 0)

    member_info = ""
    if role_config.get('useInfo', False) and (occupation or goal):
        member_info = "\n【メンバー情報】"
        if occupation:
            member_info += f"\n・職業: {occupation}"
        if goal:
            member_info += f"\n・目標: {goal}"

    past_reports_info = ""
    if past_reports:
        past_reports_info = "\n\n【過去の報告】"
        for past_report in reversed(past_reports[-2:]):  # 直近2週分のみ使用
            past_rating = past_report.get('rating', {})
            past_reports_info += f"\n[{past_report.get('weekString', '')}]"
            past_reports_info += f"\n・ストレス度: {parse_rating_level(past_rating.get('stress', 0))} ({past_rating.get('stress', 0)}/5)"
            past_reports_info += f"\n・タスク目標の達成度: {parse_rating_level(past_rating.get('achievement', 0))} ({past_rating.get('achievement', 0)}/5)"
            past_reports_info += f"\n・残業時間: {past_report.get('overtimeHours', 0)}時間/週"
            improvements = past_report.get('improvements', '')
            if improvements:
                past_reports_info += f"\n・改善施策: {improvements}"

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
・残業時間: {overtime}時間/週{past_reports_info}"""

    prompt = f"""Human: あなたは{adviser_role}です。
週次報告へのアドバイスを提供してください。
アドバイスは重要度の高いポイントに絞って、最大420文字程度としてください。
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
Assistant:"""

    return prompt
