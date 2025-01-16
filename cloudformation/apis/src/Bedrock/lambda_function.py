import json
import os
import boto3
import logging
from typing import Dict, Any
from botocore.exceptions import ClientError
from common.utils import create_response, handle_lambda_errors, parse_request_body
from prompt_generator import create_prompt, create_summary_prompt
from bedrock_client import invoke_claude
from data_formatter import format_insights_response

# ロガーの設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
stage = os.environ.get('STAGE', 'dev')
members_table_name = f'{stage}-Members'
members_table = dynamodb.Table(members_table_name)

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
        if not body or 'report' not in body:
            return create_response(400, {'error': 'リクエストボディが無効です。'})
            
        report_content = body['report']
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
        
        advisor_role = report_content.get('advisorRole', 'default')
        logger.info(f"Execute advice: organization={member.get('organizationId')}, member={member.get('id')}, advisor={advisor_role}")
                    
        # チケットのチェックと消費
        is_available, remaining_tickets = check_and_update_advice_tickets(member, member_uuid)
        if not is_available:
            return create_response(403, {
                'error': 'アドバイスチケットが不足しています。',
                'code': 'INSUFFICIENT_TICKETS',
                'remainingTickets': remaining_tickets
            })
        
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
        return create_response(500, {
            'error': 'アドバイスの生成中にエラーが発生しました。',
            'remainingTickets': remaining_tickets
        })

def handle_summary_request(event: Dict[str, Any]) -> Dict[str, Any]:
    """サマリー生成リクエストを処理"""
    try:
        body = parse_request_body(event)
        if 'reports' not in body or not isinstance(body['reports'], list) or not body['reports']:
            return create_response(400, {'error': '有効な週次報告のリストが必要です。'})
        
        prompt = create_summary_prompt(body['reports'])
        claude_response = invoke_claude(prompt)
        result = format_insights_response(claude_response)
        
        return create_response(200, {
            'data': result,
            'error': None
        })
        
    except Exception as e:
        logger.error(f"Error processing summary request: {str(e)}")
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
