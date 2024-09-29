import json
import logging
import boto3
from boto3.dynamodb.conditions import Key
import os
import uuid
import time
from decimal import Decimal
from zoneinfo import ZoneInfo
from common.utils import create_response

print('Loading function')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# SNSクライアント
sns_client = boto3.client('sns')

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
stage = os.environ.get('STAGE', 'dev')
TIMEZONE = ZoneInfo(os.environ.get('TZ', 'UTC'))
BASE_URL = os.environ.get('BASE_URL', 'http://localhost:3000')

members_table_name = f'{stage}-Members'
organizations_table_name = f'{stage}-Organizations'
weekly_reports_table_name = f'{stage}-WeeklyReports'
organizations_table = dynamodb.Table(organizations_table_name)
members_table = dynamodb.Table(members_table_name)
weekly_reports_table = dynamodb.Table(weekly_reports_table_name)

def lambda_handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")
    try:
        http_method = event['httpMethod']
        resource = event['resource']

        if http_method == 'GET' and resource == '/public/organization':
            return handle_get_organization(event)
        elif http_method == 'POST' and resource == '/public/organization':
            return handle_post_organization(event)
        elif http_method == 'GET' and resource == '/public/weekly-report':
            return handle_get_report(event)
        elif http_method == 'POST' and resource == '/public/weekly-report':
            return handle_post_report(event)
        elif http_method == 'PUT' and resource == '/public/weekly-report':
            return handle_put_report(event)
        elif http_method == 'GET' and resource == '/public/member':
            return handle_get_member(event)
        elif http_method == 'PUT' and resource == '/public/member':
            return handle_put_member(event)
        elif http_method == 'GET' and resource == '/public/project':
            return handle_get_projects(event)
        else:
            return create_response(400, f'Unsupported method: {http_method}')
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return create_response(500, f'Internal server error: {str(e)}')

def handle_get_report(event):
    params = event.get('queryStringParameters', {}) or {}
    if not params:
        return create_response(400, 'Missing query parameters')

    if 'memberUuid' in params and 'weekString' in params:
        item = get_report(params['memberUuid'], params['weekString'])
        return create_response(200, item)
    elif 'organizationId' in params and 'weekString' in params:
        items = get_reports_by_organization(params['organizationId'], params['weekString'])
        return create_response(200, items)
    else:
        return create_response(400, 'Invalid query parameters')

def get_report(member_uuid, week_string):
    try:
        response = weekly_reports_table.get_item(
            Key={
                'memberUuid': member_uuid,
                'weekString': week_string
            }
        )
        return response.get('Item')
    except Exception as e:
        logger.error(f"Error getting report: {str(e)}", exc_info=True)
        raise e

def get_reports_by_organization(organization_id, week_string):
    try:
        response = weekly_reports_table.query(
            IndexName='OrganizationWeekIndex',
            KeyConditionExpression=Key('organizationId').eq(organization_id) & Key('weekString').eq(week_string)
        )
        return response['Items']
    except Exception as e:
        logger.error(f"Error querying reports: {str(e)}", exc_info=True)
        raise e

def handle_post_report(event):
    report_data = json.loads(event['body'])
    item = prepare_item(report_data)
    response = weekly_reports_table.put_item(Item=item)
    logger.info(f"DynamoDB response: {response}")
    
    # 組織の管理者に通知を送信
    send_push_notification_to_admins(item['organizationId'], 'new_report', item)

    return create_response(201, 'Weekly report created successfully')

def handle_put_report(event):
    report_data = json.loads(event['body'])
    member_uuid = report_data.get('memberUuid')
    week_string = report_data.get('weekString')

    if not member_uuid or not week_string:
        return create_response(400, 'Missing memberUuid or weekString')

    try:
        existing_report = get_report(member_uuid, week_string)
        if not existing_report:
            return create_response(404, 'Report not found')

        updated_item = prepare_item(report_data, existing_report)
        response = weekly_reports_table.put_item(Item=updated_item)
        logger.info(f"DynamoDB response: {response}")
        
        # 組織の管理者に通知を送信
        send_push_notification_to_admins(updated_item['organizationId'], 'updated_report', updated_item)

        return create_response(200, 'Weekly report updated successfully')
    except Exception as e:
        logger.error(f"Error updating report: {str(e)}", exc_info=True)
        return create_response(500, f'Failed to update report: {str(e)}')

def float_to_decimal(obj):
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: float_to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [float_to_decimal(v) for v in obj]
    return obj

def prepare_item(report_data, existing_report=None):
    current_time = int(time.time())

    item = {
        'memberUuid': report_data.get('memberUuid'),
        'weekString': report_data.get('weekString'),
        'organizationId': report_data.get('organizationId'),
        'projects': report_data.get('projects'),
        'overtimeHours': float_to_decimal(report_data.get('overtimeHours')),
        'issues': report_data.get('issues'),
        'improvements': report_data.get('improvements'),
        'rating': report_data.get('rating', {}),
        'status': report_data.get('status'),
        'feedbacks': report_data.get('feedbacks', []),
        'approvedAt': report_data.get('approvedAt'),
        'createdAt': current_time
    }
    
    if existing_report:
        # 既存のレポートの内容を保持しつつ、新しいデータで上書き
        existing_report.update(item)
        return existing_report
    
    return item

def handle_get_member(event):
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

def get_member(member_uuid):
    try:
        response = members_table.get_item(
            Key={
                'memberUuid': member_uuid
            }
        )
        return response.get('Item')
    except Exception as e:
        logger.error(f"Error getting member: {str(e)}", exc_info=True)
        return None

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

def handle_get_projects(event):
    params = event.get('queryStringParameters', {}) or {}
    if 'memberUuid' not in params:
        return create_response(400, {'message': 'Missing memberUuid parameter'})
    
    projects = get_member_projects(params['memberUuid'])
    return create_response(200, projects)

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

def handle_put_member(event):
    data = json.loads(event['body'])
    if 'memberUuid' in data:
        if 'projects' in data:
            update_member_projects(data['memberUuid'], data['projects'])
            return create_response(200, {'message': 'Member projects updated successfully'})
        else:
            member = get_member(data['memberUuid'])
            member.update(data)
            item = prepare_member_item(member)
            response = members_table.put_item(Item=item)
            logger.info(f"Member update response: {response}")
            return create_response(200, {'message': 'Member updated successfully'})
    elif 'verifyEmail' in data:
        return handle_verify_email(data)
    else:
        return create_response(400, {'message': 'Invalid data structure'})

def prepare_member_item(member_data):
    return {
        'memberUuid': member_data.get('memberUuid', str(uuid.uuid4())),
        'id': member_data.get('id'),
        'organizationId': member_data['organizationId'],
        'name': member_data.get('name'),
        'email': member_data.get('email'),
        'goal': member_data.get('goal'),
        'projects': member_data.get('projects', [])
    }

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

def handle_verify_email(data):
    if 'memberUuid' in data:
        member = get_member(data['memberUuid'])
        member['mailConfirmed'] = True
        response = members_table.put_item(Item=member)
        logger.info(f"Member update response: {response}")
        return create_response(200, {'message': 'Member email verified successfully'})
    else:
        return create_response(400, {'message': 'Invalid data structure'})

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

def prepare_organization_item(org_data):
    return {
        'organizationId': org_data.get('organizationId'),
        'name': org_data.get('name'),
        'sender': org_data.get('sender'),
        'senderName': org_data.get('senderName'),
        'requestEnabled': org_data.get('requestEnabled'),
        'requestTime': org_data.get('requestTime'),
        'requestDayOfWeek': org_data.get('requestDayOfWeek'),
        'reportWeek': org_data.get('reportWeek')
    }

def handle_get_organization(event):
    params = event.get('queryStringParameters', {}) or {}
    if 'organizationId' in params:
        org = get_organization(params['organizationId'])
        return create_response(200, org)
    else:
        return create_response(400, {'message': 'Invalid data structure'})

def handle_post_organization(event):
    data = json.loads(event['body'])
    if 'organizationId' in data:
        item = prepare_organization_item(data)
        response = organizations_table.put_item(Item=item)
        return create_response(201, {'message': 'Organization created successfully'})
    else:
        return create_response(400, {'message': 'Invalid data structure'})

def send_push_notification_to_admins(organization_id, notification_type, report_data):
    try:
        organization = organizations_table.get_item(Key={'organizationId': organization_id})
        admin_subscriptions = organization['Item'].get('adminSubscriptions', {})
        
        notification = {
            'type': notification_type,
            'reportData': {
                'memberUuid': report_data['memberUuid'],
                'weekString': report_data['weekString'],
                'status': report_data['status']
            }
        }
        
        for admin_id, endpoint_arn in admin_subscriptions.items():
            try:
                sns_client.publish(
                    TargetArn=endpoint_arn,
                    Message=json.dumps({
                        'default': json.dumps(notification),
                        'GCM': json.dumps({
                            'notification': {
                                'title': '週次報告',
                                'body': f'{notification_type}: {report_data["weekString"]}',
                                #'click_action': 'FLUTTER_NOTIFICATION_CLICK', # Flutterアプリの場合
                                'sound': 'default'
                            },
                            'data': {
                                'type': notification_type,
                                'weekString': report_data['weekString'],
                                'status': report_data['status'],
                                'memberUuid': report_data['memberUuid']
                            }
                        })
                    }),
                    MessageStructure='json'
                )
            except Exception as e:
                logger.error(f"Error sending push notification to admin {admin_id}: {e}")
                # エンドポイントが無効な場合は削除
                if 'EndpointDisabled' in str(e):
                    remove_admin_subscription(organization_id, admin_id)
    
    except Exception as e:
        logger.error(f"Error in send_push_notification_to_admins: {str(e)}", exc_info=True)

def remove_admin_subscription(organization_id, admin_id):
    try:
        organizations_table.update_item(
            Key={'organizationId': organization_id},
            UpdateExpression="REMOVE adminSubscriptions.#adminId",
            ExpressionAttributeNames={'#adminId': admin_id}
        )
    except Exception as e:
        logger.error(f"Error removing admin subscription: {str(e)}")