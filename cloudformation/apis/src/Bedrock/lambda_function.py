import json
import os
import boto3
import logging
from datetime import datetime, timedelta
from typing import Dict, Any
from botocore.exceptions import ClientError
from decimal import Decimal
from common.utils import create_response, handle_lambda_errors, parse_request_body, decimal_default_proc
from prompt_generator import create_prompt, create_summary_prompt
from bedrock_client import invoke_claude
from data_formatter import format_insights_response
from zoneinfo import ZoneInfo
import traceback

# ロガーの設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
stage = os.environ.get('STAGE', 'dev')
members_table_name = f'{stage}-Members'
weekly_reports_table_name = f'{stage}-WeeklyReports'
members_table = dynamodb.Table(members_table_name)
weekly_reports_table = dynamodb.Table(weekly_reports_table_name)
TIMEZONE = ZoneInfo(os.environ.get('TZ', 'UTC'))

@handle_lambda_errors
def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda関数のメインハンドラー"""
    try:
        # パスの取得
        resource = event['resource']
        
        if resource == '/bedrock/advice':
            return handle_advice_request(event)
        elif resource == '/bedrock/summary':
            return handle_summary_request(event)
        else:
            return create_response(404, {'error': '無効なパスです。'})
            
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return create_response(500, {
            'error': 'リクエスト処理中にエラーが発生しました。'
        })

def handle_advice_request(event: Dict[str, Any]) -> Dict[str, Any]:
    """アドバイス生成リクエストを処理"""
    remaining_tickets = 0
    try:
        body = parse_request_body(event)
        member_uuid = body.get('memberUuid')
        week_string = body.get('weekString')
        advisor_role = body.get('advisorRole', 'manager')

        if not member_uuid:
            return create_response(400, {'error': 'memberUuidが必要です。'})
        if not week_string:
            return create_response(400, {'error': 'weekStringが必要です。'})

        # メンバー情報を取得
        response = members_table.get_item(
            Key={'memberUuid': member_uuid}
        )
        member = response.get('Item')
        if not member:
            raise Exception('Member not found')
        
        logger.info(f"Execute advice: organization={member.get('organizationId')}, member={member.get('id')}, advisor={advisor_role}")
        
        # チケットのチェックと消費
        is_available, remaining_tickets = check_and_update_advice_tickets(member, member_uuid)
        if not is_available:
            return create_response(403, {
                'error': 'アドバイスチケットが不足しています。',
                'code': 'INSUFFICIENT_TICKETS',
                'remainingTickets': remaining_tickets
            })

        report_content = get_report(member_uuid, week_string)

        # プロンプトの生成と実行
        prompt = create_prompt(report_content, member)
        claude_response = invoke_claude(prompt)
        formatted_advice = claude_response.strip()

        return create_response(200, {
            'advice': formatted_advice,
            'weekString': report_content.get('weekString'),
            'memberUuid': member_uuid,
            'remainingTickets': remaining_tickets
        })
        
    except Exception as e:
        logger.error(f"Error in handle_advice_request: {str(e)}")
        logger.error(traceback.format_exc())
        return create_response(500, {
            'error': 'アドバイスの生成中にエラーが発生しました。',
            'remainingTickets': remaining_tickets
        })

def handle_summary_request(event: Dict[str, Any]) -> Dict[str, Any]:
    """サマリー生成リクエストを処理"""
    try:
        body = parse_request_body(event)
        member_uuid = body.get('memberUuid')
        if not member_uuid:
            return create_response(400, {'error': 'memberUuidが必要です。'})
        
        reports = get_member_reports(member_uuid)

        prompt = create_summary_prompt(reports)
        claude_response = invoke_claude(prompt)
        result = format_insights_response(claude_response)
        
        return create_response(200, {
            'data': result,
            'error': None
        })
        
    except Exception as e:
        logger.error(f"Error processing summary request: {str(e)}")
        logger.error(traceback.format_exc())
        return create_response(500, {'error': 'サマリーの生成中にエラーが発生しました。'})
    
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

def get_report(member_uuid, week_string):
    try:
        response = weekly_reports_table.get_item(
            Key={
                'memberUuid': member_uuid,
                'weekString': week_string
            }
        )
        item = response.get('Item')
        if item:
            return json.loads(
                json.dumps(item, default=decimal_default_proc)
            )
        return None
    except Exception as e:
        logger.error(f"Error getting report: {str(e)}", exc_info=True)
        return None

def get_member_reports(member_uuid):
    weeks = get_last_5_weeks()
    reports = []
    
    for week in weeks:
        report = get_report(member_uuid, week)
        if report:
            reports.append(report)
        else:
            reports.append({
                'memberUuid': member_uuid,
                'weekString': week,
                'status': 'none'
            })
    return reports

def get_last_5_weeks():
    """5週前から先週までの週番号を取得（今週は含まない）
    Returns:
        list: ['YYYY-WNN'形式の週番号文字列のリスト（古い順）]
    """
    today = datetime.now(TIMEZONE)
    
    def get_iso_week(date):
        return date.isocalendar()[:2]  # (year, week)を返す
    
    # 先週の月曜日を取得
    last_monday = today - timedelta(days=today.weekday() + 7)
    weeks = []
    
    # 5週前から先週までの週番号を取得
    for i in range(4, -1, -1):  # 4,3,2,1,0 の順で処理（新しい順）
        target_date = last_monday - timedelta(weeks=i)
        year, week = get_iso_week(target_date)
        weeks.append(f"{year}-W{week:02d}")
    
    return weeks  # 古い順に自然と並ぶ