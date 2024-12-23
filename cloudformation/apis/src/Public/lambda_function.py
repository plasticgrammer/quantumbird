import json
import logging
import boto3
from boto3.dynamodb.conditions import Key
import os
from zoneinfo import ZoneInfo
import common.publisher
from common.utils import create_response
import common.dynamo_items as dynamo_items
from common.cognito_util import get_admin_emails

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

# 定数の追加（ファイル先頭の定数定義部分に追加）
ADVICE_TICKETS_MAX = 3
ADVICE_TICKETS_INCREMENT = 3

# Cognitoクライアントの初期化
USER_POOL_REGION = os.environ.get('USER_POOL_REGION', 'ap-southeast-2')
cognito = boto3.client('cognito-idp', region_name=USER_POOL_REGION)
USER_POOL_ID = os.environ.get('USER_POOL_ID')

def lambda_handler(event, context):
    #logger.info(f"Received event: {json.dumps(event)}")
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
    item = dynamo_items.prepare_weekly_report_item(report_data)
    
    try:
        member_uuid = item['memberUuid']
        member = get_member(member_uuid)
        if not member:
            return create_response(404, 'Member not found')
        
        current_tickets = member.get('adviceTickets', 0)
        # MAX以上の場合はそのまま、それ以外の場合は加算して最大値制限
        if current_tickets < ADVICE_TICKETS_MAX:
            member['adviceTickets'] = min(current_tickets + ADVICE_TICKETS_INCREMENT, ADVICE_TICKETS_MAX)
        
        # トランザクションで両方のテーブルを更新
        transaction_items = [
            {
                'Put': {
                    'TableName': weekly_reports_table.name,
                    'Item': item
                }
            },
            {
                'Put': {
                    'TableName': members_table.name,
                    'Item': member
                }
            }
        ]
        
        dynamodb.meta.client.transact_write_items(
            TransactItems=transaction_items
        )
        
        send_push_notification_to_admins(item['organizationId'], 'new_report', item)
        
        return create_response(201, {
            'message': 'Weekly report created successfully',
            'adviceTickets': member['adviceTickets']
        })
        
    except Exception as e:
        logger.error(f"Error in transaction: {str(e)}", exc_info=True)
        return create_response(500, f'Transaction failed: {str(e)}')

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

        updated_item = dynamo_items.prepare_weekly_report_item(report_data, existing_report)
        response = weekly_reports_table.put_item(Item=updated_item)
        
        # 組織の管理者に通知を送信
        send_push_notification_to_admins(updated_item['organizationId'], 'updated_report', updated_item)

        return create_response(200, 'Weekly report updated successfully')
    except Exception as e:
        logger.error(f"Error updating report: {str(e)}", exc_info=True)
        return create_response(500, f'Failed to update report: {str(e)}')

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
            if not member:
                return create_response(404, {'message': 'Member not found'})
            item = dynamo_items.prepare_member_item(data, member)
            response = members_table.put_item(Item=item)
            return create_response(200, {'message': 'Member updated successfully'})
    elif 'verifyEmail' in data:
        return handle_verify_email(data)
    else:
        return create_response(400, {'message': 'Invalid data structure'})

def update_member_projects(member_uuid, projects):
    try:
        # 既存のメンバー情報を取得
        member = get_member(member_uuid)
        if not member:
            raise Exception('Member not found')

        # プロジェクトリストを重複なしで更新
        projects = list(dict.fromkeys(projects))  # 順序を保持しながら重複を削除

        response = members_table.update_item(
            Key={'memberUuid': member_uuid},
            UpdateExpression="SET projects = :p",
            ExpressionAttributeValues={':p': projects},
            ReturnValues="UPDATED_NEW"
        )
        return response
    except Exception as e:
        logger.error(f"Error updating member projects: {str(e)}", exc_info=True)
        raise e

def handle_verify_email(data):
    if 'memberUuid' in data:
        member = get_member(data['memberUuid'])
        member['mailConfirmed'] = True
        response = members_table.put_item(Item=member)
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
        item = dynamo_items.prepare_organization_item(data)
        response = organizations_table.put_item(Item=item)
        return create_response(201, {'message': 'Organization created successfully'})
    else:
        return create_response(400, {'message': 'Invalid data structure'})

def join_url_paths(*parts):
    """Join URL parts ensuring proper forward slashes"""
    return '/'.join(str(p).strip('/') for p in parts)

def send_push_notification_to_admins(organization_id, notification_type, report_data):
    try:
        organization = organizations_table.get_item(Key={'organizationId': organization_id})
        org_item = organization['Item']
        features = org_item.get('features', {})
        admin_subscriptions = features.get('notifySubscriptions', {})
        
        # プッシュ通知とメール通知の内容を準備
        notification = {
            'type': notification_type,
            'reportData': {
                'memberUuid': report_data['memberUuid'],
                'weekString': report_data['weekString'],
                'status': report_data['status']
            }
        }

        # メール通知用の内容を準備
        member = get_member(report_data['memberUuid'])
        if not member:
            logger.error(f"Member not found: {report_data['memberUuid']}")
            return

        sendFrom = common.publisher.get_from_address(org_item)
        subject = "【週次報告システム】新しい報告が提出されました"
        bodyText = f"組織名：{org_item['name']}\n\n"
        bodyText += f"{member.get('name', '-')}さん が {report_data['weekString']} の週次報告を提出しました。\n\n"
        bodyText += "下記リンクより報告内容をご確認ください。\n"
        
        # 管理者確認用のリンクを生成
        admin_link = join_url_paths(BASE_URL, 'admin/reports', report_data['weekString'])
        bodyText += admin_link

        # 管理者へのメール送信処理
        if features.get('notifyByEmail'):
            # get_admin_emailsをcognito_utilから使用
            admin_emails = get_admin_emails(USER_POOL_ID, organization_id, cognito)
            if (admin_emails):
                try:
                    logger.info(f"Send mail from: {sendFrom}, to: {admin_emails}")
                    common.publisher.send_mail(sendFrom, admin_emails, subject, bodyText)
                except Exception as e:
                    logger.error(f"Error sending admin notification email: {str(e)}", exc_info=True)
            else:
                logger.warning(f"No admin emails found for organization: {organization_id}")

        # プッシュ通知の送信（既存のコード）
        for admin_id, endpoint_arn in admin_subscriptions.items():
            try:
                sns_client.publish(
                    TargetArn=endpoint_arn,
                    Message=json.dumps({
                        'default': json.dumps(notification),
                        'GCM': json.dumps({
                            'notification': {
                                'title': f'[{organization_id}] 週次報告',
                                'body': f'{notification_type}: {report_data["weekString"]}',
                                #'click_action': 'FLUTTER_NOTIFICATION_CLICK', # Flutterアプリの場合
                                'sound': 'default'
                            },
                            'data': {
                                'type': notification_type,
                                'organizationId': organization_id,
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
            UpdateExpression="REMOVE notifySubscriptions.#adminId",
            ExpressionAttributeNames={'#adminId': admin_id}
        )
    except Exception as e:
        logger.error(f"Error removing admin subscription: {str(e)}")