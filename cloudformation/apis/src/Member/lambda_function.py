import json
import logging
import boto3
from boto3.dynamodb.conditions import Key
import os
import uuid
from decimal import Decimal
from common.utils import create_response
import common.dynamo_items as dynamo_items
import common.publisher
import urllib.parse

print('Loading function')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
stage = os.environ.get('STAGE', 'dev')
base_url = os.environ.get('BASE_URL', 'http://localhost:3000/')
members_table_name = f'{stage}-Members'
members_table = dynamodb.Table(members_table_name)
organizations_table_name = f'{stage}-Organizations'
organizations_table = dynamodb.Table(organizations_table_name)
weekly_reports_table_name = f'{stage}-WeeklyReports'
weekly_reports_table = dynamodb.Table(weekly_reports_table_name)

def get_organization(organization_id):
    try:
        response = organizations_table.get_item(
            Key={
                'organizationId': organization_id
            }
        )
        return response.get('Item')
    except Exception as e:
        logger.error(f"Error getting organization: {str(e)}", exc_info=True)
        return None

def float_to_decimal(obj):
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: float_to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [float_to_decimal(v) for v in obj]
    return obj

def lambda_handler(event, context):
    #logger.info(f"Received event: {json.dumps(event)}")
    try:
        http_method = event['httpMethod']
        resource = event['resource']

        if resource == '/member/project' and http_method == 'GET':
            return handle_get_projects(event)
        elif resource == '/member/mail' and http_method == 'PUT':
            return handle_put_email_confirmed(event)
        elif resource == '/member':
            if http_method == 'GET':
                return handle_get(event)
            elif http_method == 'POST':
                return handle_post(event)
            elif http_method == 'PUT':
                return handle_put(event)
            elif http_method == 'DELETE':
                return handle_delete(event)
        
        return create_response(400, {'message': f'Unsupported method: {http_method} or resource: {resource}'})
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return create_response(500, {'message': f'Internal server error: {str(e)}'})

def handle_get_projects(event):
    params = event.get('queryStringParameters', {}) or {}
    if 'memberUuid' not in params:
        return create_response(400, {'message': 'Missing memberUuid parameter'})
    
    projects = get_member_projects(params['memberUuid'])
    return create_response(200, projects)

def handle_get(event):
    params = event.get('queryStringParameters', {}) or {}
    if not params:
        return create_response(400, {'message': 'Missing query parameters'})

    if 'memberUuid' in params:
        member = get_member(params['memberUuid'])
        return create_response(200, member)
    elif 'organizationId' in params:
        members = list_members(params['organizationId'])
        return create_response(200, members)
    else:
        return create_response(400, {'message': 'Invalid query parameters'})

def handle_post(event):
    data = json.loads(event['body'])
    if 'memberUuid' not in data:
        data['memberUuid'] = str(uuid.uuid4())
    
    try:
        organization = get_organization(data['organizationId'])
        if not organization:
            return create_response(404, {'message': 'Organization not found'})
            
        item = dynamo_items.prepare_member_item(data)
        item['emailConfirmed'] = False
        
        members_table.put_item(Item=item)
        
        # 確認メールの送信
        send_confirmation_email(organization, item)
        
        return create_response(201, {'message': 'Member created successfully'})
    except Exception as e:
        logger.error(f"Error creating member: {str(e)}", exc_info=True)
        return create_response(500, {'message': str(e)})

def send_confirmation_email(organization, member):
    """メンバーに確認メールを送信する"""
    try:
        if not member.get('email'):
            logger.warning(f"No email address for member: {member.get('id', 'Unknown ID')}")
            return

        sendFrom = common.publisher.get_from_address(organization)
        subject = "【週次報告システム】メンバー登録設定完了のご連絡"
        bodyText = "週次報告システムの送信先に登録されました。\n"
        bodyText += f"組織名：{organization['name']}\n\n"
        bodyText += "※本メールは、登録した際に配信される自動配信メールです。\n"

        url = urllib.parse.urljoin(base_url, f"member/mail/{urllib.parse.quote(member['memberUuid'])}")
        bodyText += "\n到達確認のため下記リンクをクリックしてください。\n"
        bodyText += url

        common.publisher.send_mail(sendFrom, [member['email']], subject, bodyText)
        logger.info(f"Sent confirmation email to {member['email']}")
    except Exception as e:
        logger.error(f"Failed to send confirmation email: {str(e)}")
        raise

def handle_put(event):
    data = json.loads(event['body'])
    if 'memberUuid' not in data:
        return create_response(400, {'message': 'memberUuid is required'})

    try:
        member_uuid = data['memberUuid']
        existing_member = get_member(member_uuid)
        
        if existing_member is None:
            return create_response(404, {'message': f'Member with UUID {member_uuid} not found'})

        # メールアドレスが変更されたかチェック
        email_changed = (data.get('email') and 
                        data['email'] != existing_member.get('email'))

        # メールアドレスが変更された場合は未確認状態に
        if email_changed:
            data['emailConfirmed'] = False

        # メンバー情報を更新
        item = dynamo_items.prepare_member_item(data, existing_member)
        members_table.put_item(Item=item)

        # メールアドレスが変更された場合は確認メールを再送信
        if email_changed:
            organization = get_organization(item['organizationId'])
            if organization:
                send_confirmation_email(organization, item)

        return create_response(200, {'message': 'Member updated successfully'})
    except Exception as e:
        logger.error(f"Error updating member: {str(e)}", exc_info=True)
        return create_response(500, {'message': str(e)})

def handle_put_email_confirmed(event):
    data = json.loads(event['body'])
    if 'memberUuid' in data:
        member_uuid = data['memberUuid']
        member = get_member(member_uuid)        
        if member is None:
            return create_response(404, {'message': f'Member with UUID {member_uuid} not found'})

        member['emailConfirmed'] = True
        response = members_table.put_item(Item=member)
        return create_response(200, {
            'message': 'Member email verified successfully',
            'email': member['email']
        })
    else:
        return create_response(400, {'message': 'Invalid data structure'})

def handle_delete(event):
    params = event.get('queryStringParameters', {}) or {}
    if 'memberUuid' in params:
        delete_member(params['memberUuid'])
        return create_response(200, {'message': 'Member deleted successfully'})
    else:
        return create_response(400, {'message': 'Missing required parameters'})

def get_member(member_uuid):
    try:
        response = members_table.get_item(
            Key={
                'memberUuid': member_uuid
            }
        )
        item = response.get('Item')
        if item is None:
            logger.warning(f"Member with UUID {member_uuid} not found")
        return item
    except Exception as e:
        logger.error(f"Error getting member: {str(e)}", exc_info=True)
        raise e

def get_member_projects(member_uuid):
    try:
        response = members_table.get_item(
            Key={
                'memberUuid': member_uuid
            },
            ProjectionExpression='projects'
        )
        return response.get('Item', {}).get('projects', [])
    except Exception as e:
        logger.error(f"Error getting member projects: {str(e)}", exc_info=True)
        raise e

def list_members(organization_id):
    try:
        response = members_table.query(
            IndexName='OrganizationIndex',
            KeyConditionExpression=Key('organizationId').eq(organization_id)
        )
        members = response['Items']
        # IDの昇順でソート
        sorted_members = sorted(members, key=lambda x: x.get('id', ''))
        return sorted_members
    except Exception as e:
        logger.error(f"Error listing members: {str(e)}", exc_info=True)
        raise e

def update_member_projects(member_uuid, projects):
    try:
        response = members_table.update_item(
            Key={'memberUuid': member_uuid},
            UpdateExpression="SET projects = :p",
            ExpressionAttributeValues={':p': projects},
            ReturnValues="UPDATED_NEW"
        )
        logger.info(f"Update member projects response: {response}")
        return response
    except Exception as e:
        logger.error(f"Error updating member projects: {str(e)}", exc_info=True)
        raise e

def delete_member(member_uuid):
    try:
        # メンバーの週次レポートを全て削除
        delete_member_reports(member_uuid)
        
        # メンバー情報を削除
        members_table.delete_item(
            Key={
                'memberUuid': member_uuid
            }
        )
    except Exception as e:
        logger.error(f"Error deleting member: {str(e)}", exc_info=True)
        raise e

def delete_member_reports(member_uuid):
    """メンバーの全週次レポートを削除する"""
    try:
        # メンバーの全レポートを取得
        reports = []
        last_evaluated_key = None
        
        while True:
            if last_evaluated_key:
                response = weekly_reports_table.query(
                    KeyConditionExpression=Key('memberUuid').eq(member_uuid),
                    ExclusiveStartKey=last_evaluated_key
                )
            else:
                response = weekly_reports_table.query(
                    KeyConditionExpression=Key('memberUuid').eq(member_uuid)
                )
            
            # 見つかったレポートを削除
            for item in response.get('Items', []):
                weekly_reports_table.delete_item(
                    Key={
                        'memberUuid': member_uuid,
                        'weekString': item['weekString']
                    }
                )
            
            last_evaluated_key = response.get('LastEvaluatedKey')
            if not last_evaluated_key:
                break
                
        logger.info(f"Deleted all reports for member: {member_uuid}")
    except Exception as e:
        logger.error(f"Error deleting member reports: {str(e)}", exc_info=True)
        raise e
