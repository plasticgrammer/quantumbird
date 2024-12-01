import json
import logging
import boto3
import urllib.parse
import os
import uuid
import common.publisher
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
from common.utils import create_response

print('Loading function')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

stage = os.environ.get('STAGE', 'dev')
BASE_URL = os.environ.get('BASE_URL', 'http://localhost:3000')
WEB_PUSH_PLATFORM_ARN = os.environ['WEB_PUSH_PLATFORM_ARN']

# SNSクライアント
sns_client = boto3.client('sns')

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
organizations_table_name = f'{stage}-Organizations'
members_table_name = f'{stage}-Members'
reports_table_name = f'{stage}-WeeklyReports'
user_tasks_table_name = f'{stage}-UserTasks'
organizations_table = dynamodb.Table(organizations_table_name)
members_table = dynamodb.Table(members_table_name)
reports_table = dynamodb.Table(reports_table_name)
user_tasks_table = dynamodb.Table(user_tasks_table_name)

def lambda_handler(event, context):
    #logger.info(f"Received event: {json.dumps(event)}")
    try:
        http_method = event['httpMethod']
        resource = event['resource']

        if resource == '/organization':
            if http_method == 'GET':
                return handle_get(event)
            elif http_method == 'POST':
                return handle_post(event)
            elif http_method == 'PUT':
                return handle_put(event)
            elif http_method == 'DELETE':
                return handle_delete(event)
        elif resource == '/organization/push-subscription':
            if http_method == 'GET':
                return handle_get_subscription(event)
            elif http_method == 'POST':
                return handle_push_subscription(event)
            elif http_method == 'DELETE':
                return handle_remove_subscription(event)

        return create_response(400, {'message': f'Unsupported resource or method: {http_method} {resource}'})
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return create_response(500, {'message': f'Internal server error: {str(e)}'})

def handle_get_subscription(event):
    params = event.get('queryStringParameters', {}) or {}
    organization_id = params.get('organizationId')
    admin_id = params.get('adminId')

    if not organization_id or not admin_id:
        return create_response(400, {'message': 'Missing required parameters: organizationId or adminId'})

    try:
        endpoint_arn = get_existing_subscription(organization_id, admin_id)
        return create_response(200, {'endpointArn': endpoint_arn})
    except Exception as e:
        logger.error(f"Error getting subscription: {str(e)}", exc_info=True)
        return create_response(500, {'message': 'Failed to get subscription'})

def get_existing_subscription(organization_id, admin_id):
    try:
        response = organizations_table.get_item(
            Key={'organizationId': organization_id},
            ProjectionExpression='adminSubscriptions'
        )
        admin_subscriptions = response.get('Item', {}).get('adminSubscriptions', {})
        return admin_subscriptions.get(admin_id)
    except Exception as e:
        logger.error(f"Error getting existing subscription: {str(e)}", exc_info=True)
        return None

def handle_get(event):
    params = event.get('queryStringParameters', {}) or {}
    if 'organizationId' in params:
        org = get_organization(params['organizationId'])
        if org is None:
            return create_response(404, {'message': f"Organization with id {params['organizationId']} not found"})
        members = list_members(params['organizationId'])
        org['members'] = sorted(members, key=lambda x: x.get('id', ''))
        return create_response(200, org)
    elif 'memberUuid' in params:
        member = get_member(params['memberUuid'])
        if member is None:
            return create_response(404, {'message': f"Member with uuid {params['memberUuid']} not found"})
        return create_response(200, member)
    else:
        orgs = list_organizations()
        return create_response(200, orgs)

def handle_post(event):
    data = json.loads(event['body'])
    if 'organizationId' in data:
        item = prepare_organization_item(data)
        response = organizations_table.put_item(Item=item)
        return create_response(201, {'message': 'Organization created successfully'})
    elif 'memberUuid' in data:
        item = prepare_member_item(data)
        response = members_table.put_item(Item=item)
        return create_response(201, {'message': 'Member created successfully'})
    else:
        return create_response(400, {'message': 'Invalid data structure'})

def handle_put(event):
    data = json.loads(event['body'])
    if 'organizationId' in data:
        existing_org = get_organization(data['organizationId'])
        
        if existing_org is None:
            existing_org = {}
            
        org_item = prepare_organization_item(data, existing_org)
        organizations_table.put_item(Item=org_item)

        if 'members' in data:
            update_members(data['organizationId'], data['members'])

        return create_response(200, {'message': 'Organization and members updated successfully'})
    elif 'memberUuid' in data:
        existing_member = get_member(data['memberUuid'])
        item = prepare_member_item(data, existing_member)
        response = members_table.put_item(Item=item)
        return create_response(200, {'message': 'Member updated successfully'})
    else:
        return create_response(400, {'message': 'Invalid data structure'})

def handle_delete(event):
    params = event.get('queryStringParameters', {}) or {}
    if 'organizationId' not in params:
        return create_response(400, {'message': 'Missing required parameter: organizationId'})

    organization_id = params['organizationId']
    mode = params.get('mode')

    try:
        if mode == 'complete':
            # 完全削除モード
            delete_organization_completely(organization_id)
            return create_response(200, {'message': 'Organization and all related data deleted successfully'})
        else:
            # 通常の削除モード（既存の処理）
            delete_organization(organization_id)
            return create_response(200, {'message': 'Organization and its members deleted successfully'})
    except Exception as e:
        logger.error(f"Error deleting organization: {str(e)}", exc_info=True)
        return create_response(500, {'message': f'Failed to delete organization: {str(e)}'})

def delete_organization(organization_id):
    """組織のデータを削除する"""
    try:
        logger.info(f"Starting deletion for organization: {organization_id}")

        # 1. プッシュ通知登録の削除
        delete_push_subscriptions(organization_id)
        logger.info(f"Deleted push subscriptions for organization: {organization_id}")

        # 2. 組織データの削除
        organizations_table.delete_item(
            Key={
                'organizationId': organization_id
            }
        )
        logger.info(f"Deleted organization data for: {organization_id}")

    except Exception as e:
        logger.error(f"Error in deletion process: {str(e)}", exc_info=True)
        raise Exception(f"Failed to delete organization: {str(e)}")

def delete_organization_completely(organization_id):
    """組織に関連する全てのデータを完全に削除する"""
    try:
        logger.info(f"Starting complete deletion for organization: {organization_id}")

        # 1. プッシュ通知登録の削除
        delete_push_subscriptions(organization_id)
        logger.info(f"Deleted push subscriptions for organization: {organization_id}")

        # 2. 週次報告データの削除
        delete_weekly_reports(organization_id)
        logger.info(f"Deleted weekly reports for organization: {organization_id}")

        # 3. ユーザータスクの削除
        delete_user_tasks(organization_id)
        logger.info(f"Deleted user tasks for organization: {organization_id}")

        # 4. メンバーデータの削除
        delete_members_by_organization(organization_id)
        logger.info(f"Deleted members for organization: {organization_id}")

        # 5. 組織データの削除
        organizations_table.delete_item(
            Key={
                'organizationId': organization_id
            }
        )
        logger.info(f"Deleted organization data for: {organization_id}")

    except Exception as e:
        logger.error(f"Error in complete deletion process: {str(e)}", exc_info=True)
        raise Exception(f"Failed to completely delete organization: {str(e)}")
    
def delete_weekly_reports(organization_id):
    """週次報告データの削除（ページネーション対応）"""
    try:
        logger.info(f"Starting deletion of weekly reports for organization: {organization_id}")
        
        last_evaluated_key = None
        total_deleted = 0

        while True:
            # クエリパラメータの準備
            query_params = {
                'IndexName': 'OrganizationWeekIndex',
                'KeyConditionExpression': Key('organizationId').eq(organization_id)
            }
            if last_evaluated_key:
                query_params['ExclusiveStartKey'] = last_evaluated_key

            # 週次報告の取得
            response = reports_table.query(**query_params)
            items = response.get('Items', [])

            if not items:
                break

            # バッチ削除の実行
            with reports_table.batch_writer() as batch:
                for item in items:
                    batch.delete_item(
                        Key={
                            'memberUuid': item['memberUuid'],
                            'weekString': item['weekString']
                        }
                    )
                    total_deleted += 1

            # 次のページがあるか確認
            last_evaluated_key = response.get('LastEvaluatedKey')
            if not last_evaluated_key:
                break

        logger.info(f"Deleted {total_deleted} weekly reports for organization: {organization_id}")
        return total_deleted

    except Exception as e:
        logger.error(f"Error deleting weekly reports: {str(e)}", exc_info=True)
        raise

def delete_user_tasks(organization_id):
    """組織に関連するユーザータスクの削除"""
    try:
        logger.info(f"Starting deletion of user tasks for organization: {organization_id}")
        
        # まず組織のメンバー一覧を取得
        members = list_members(organization_id)
        total_deleted = 0

        for member in members:
            member_uuid = member['memberUuid']
            last_evaluated_key = None

            while True:
                # クエリパラメータの準備
                query_params = {
                    'KeyConditionExpression': Key('userId').eq(member_uuid)
                }
                if last_evaluated_key:
                    query_params['ExclusiveStartKey'] = last_evaluated_key

                # タスクの取得
                response = user_tasks_table.query(**query_params)
                items = response.get('Items', [])

                if not items:
                    break

                # バッチ削除の実行
                with user_tasks_table.batch_writer() as batch:
                    for item in items:
                        batch.delete_item(
                            Key={
                                'userId': item['userId'],
                                'taskId': item['taskId']
                            }
                        )
                        total_deleted += 1

                # 次のページがあるか確認
                last_evaluated_key = response.get('LastEvaluatedKey')
                if not last_evaluated_key:
                    break

        logger.info(f"Deleted {total_deleted} user tasks for organization: {organization_id}")
        return total_deleted

    except Exception as e:
        logger.error(f"Error deleting user tasks: {str(e)}", exc_info=True)
        raise

def delete_members_by_organization(organization_id):
    """組織に属する全メンバーの削除"""
    try:
        members = list_members(organization_id)
        if not members:
            return 0

        with members_table.batch_writer() as batch:
            for member in members:
                batch.delete_item(
                    Key={
                        'memberUuid': member['memberUuid']
                    }
                )

        return len(members)

    except Exception as e:
        logger.error(f"Error deleting members: {str(e)}", exc_info=True)
        raise

def delete_push_subscriptions(organization_id):
    """組織のプッシュ通知登録を削除"""
    try:
        org = get_organization(organization_id)
        if not org or 'adminSubscriptions' not in org:
            return 0

        admin_subscriptions = org.get('adminSubscriptions', {})
        deleted_count = 0

        for admin_id, endpoint_arn in admin_subscriptions.items():
            try:
                sns_client.delete_endpoint(
                    EndpointArn=endpoint_arn
                )
                deleted_count += 1
            except ClientError as e:
                if e.response['Error']['Code'] != 'InvalidParameter':
                    logger.warning(f"Failed to delete SNS endpoint for admin {admin_id}: {str(e)}")
                continue

        logger.info(f"Deleted {deleted_count} push subscriptions for organization: {organization_id}")
        return deleted_count

    except Exception as e:
        logger.error(f"Error deleting push subscriptions: {str(e)}", exc_info=True)
        raise

def prepare_organization_item(org_data, existing_org=None):
    if existing_org is None:
        existing_org = {}
    
    # 既存のfeaturesを保持
    features = existing_org.get('features', {}).copy()
    
    # 新しいfeaturesがある場合は更新
    if 'features' in org_data:
        features.update(org_data['features'])
    
    updated_org = {
        'organizationId': org_data.get('organizationId', existing_org.get('organizationId')),
        'name': org_data.get('name', existing_org.get('name')),
        'sender': org_data.get('sender', existing_org.get('sender')),
        'senderName': org_data.get('senderName', existing_org.get('senderName')),
        'requestEnabled': org_data.get('requestEnabled', existing_org.get('requestEnabled')),
        'requestTime': org_data.get('requestTime', existing_org.get('requestTime')),
        'requestDayOfWeek': org_data.get('requestDayOfWeek', existing_org.get('requestDayOfWeek')),
        'reportWeek': org_data.get('reportWeek', existing_org.get('reportWeek')),
        'features': features,
        'adminSubscriptions': existing_org.get('adminSubscriptions', {})
    }
    
    if 'adminSubscriptions' in org_data:
        updated_org['adminSubscriptions'].update(org_data['adminSubscriptions'])

    return {k: v for k, v in updated_org.items() if v is not None}

def prepare_member_item(member_data, existing_member=None):
    if existing_member is None:
        existing_member = {}

    updated_member = {
        'memberUuid': member_data.get('memberUuid', existing_member.get('memberUuid', str(uuid.uuid4()))),
        'id': member_data.get('id', existing_member.get('id')),
        'organizationId': member_data.get('organizationId', existing_member.get('organizationId')),
        'name': member_data.get('name', existing_member.get('name')),
        'email': member_data.get('email', existing_member.get('email')),
        'extraInfo': member_data.get('extraInfo', existing_member.get('extraInfo', {})),
        'projects': member_data.get('projects', existing_member.get('projects', [])),
        'adviceTickets': member_data.get('adviceTickets', existing_member.get('adviceTickets', 0))
    }
    return {k: v for k, v in updated_member.items() if v is not None}

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

def list_organizations():
    try:
        response = organizations_table.scan()
        return response['Items']
    except Exception as e:
        logger.error(f"Error listing organizations: {str(e)}", exc_info=True)
        raise e

def list_members(organization_id):
    try:
        response = members_table.query(
            IndexName='OrganizationIndex',
            KeyConditionExpression=Key('organizationId').eq(organization_id)
        )
        members = response['Items']
        sorted_members = sorted(members, key=lambda x: x.get('id', ''))
        return sorted_members
    except Exception as e:
        logger.error(f"Error listing members: {str(e)}", exc_info=True)
        raise e

def update_members(organization_id, members):
    org = get_organization(organization_id)

    existing_members = list_members(organization_id)
    existing_members_dict = {m['memberUuid']: m for m in existing_members if 'memberUuid' in m}

    for member in members:
        existing_member = existing_members_dict.get(member.get('memberUuid'))
        member_item = prepare_member_item(member, existing_member)
        member_item['organizationId'] = organization_id

        is_new_member = existing_member is None
        email_changed = existing_member and existing_member.get('email') != member_item.get('email')

        if is_new_member:
            member_item['emailConfirmed'] = False
            try:
                if not member_item.get('email'):
                    logger.warning(f"No email address for new member: {member_item.get('id', 'Unknown ID')}")
                    continue
                send_registor_mail(org, member_item)
                logger.info(f"Sent registration email to new member {member_item.get('id')}")
            except Exception as e:
                logger.error(f"Failed to send registration email to new member {member_item.get('id')}: {str(e)}")
        elif email_changed:
            member_item['emailConfirmed'] = False
            try:
                if not member_item.get('email'):
                    logger.warning(f"No email address for member: {member_item.get('id', 'Unknown ID')}")
                    continue
                send_registor_mail(org, member_item)
                logger.info(f"Sent update email to member {member_item.get('id')} due to email change")
            except Exception as e:
                logger.error(f"Failed to send update email to member {member_item.get('id')}: {str(e)}")
        else:
            # メールアドレスが変更されていない場合、emailConfirmedの状態を保持
            member_item['emailConfirmed'] = existing_member.get('emailConfirmed', False)

        members_table.put_item(Item=member_item)

    # 削除されたメンバーの処理
    current_member_uuids = {m.get('memberUuid') for m in members if 'memberUuid' in m}
    for member_uuid in existing_members_dict:
        if member_uuid not in current_member_uuids:
            delete_member(member_uuid)

def send_registor_mail(organization, member):
    sendFrom = common.publisher.get_from_address(organization)
    subject = "【週次報告システム】メンバー登録設定完了のご連絡"
    bodyText = "週次報告システムの送信先に登録されました。\n"
    bodyText += f"組織名：{organization['name']}\n\n"
    bodyText += "※本メールは、登録した際に配信される自動配信メールです。\n"

    base_url = urllib.parse.urljoin(BASE_URL, "member/mail")
    path_params = [urllib.parse.quote(member['memberUuid'])]    
    # URLの構築
    url = f"{base_url}/{'/'.join(path_params)}"    
    bodyText += "\n到達確認のため下記リンクをクリックしてください。\n"
    bodyText += url

    if member.get('email'):
        common.publisher.send_mail(sendFrom, [member['email']], subject, bodyText)
    else:
        logger.warning(f"No email address found for member: {member.get('id', 'Unknown ID')}")

def delete_organization_and_members(organization_id):
    try:
        organizations_table.delete_item(
            Key={
                'organizationId': organization_id
            }
        )

        members = list_members(organization_id)
        with members_table.batch_writer() as batch:
            for member in members:
                batch.delete_item(
                    Key={
                        'memberUuid': member['memberUuid']
                    }
                )
    except Exception as e:
        logger.error(f"Error deleting organization and members: {str(e)}", exc_info=True)
        raise e

def delete_member(member_uuid):
    try:
        members_table.delete_item(
            Key={
                'memberUuid': member_uuid
            }
        )
    except Exception as e:
        logger.error(f"Error deleting member: {str(e)}", exc_info=True)
        raise e

def delete_member_by_id(organization_id, member_id):
    response = members_table.query(
        IndexName='OrganizationIndex',
        KeyConditionExpression=Key('organizationId').eq(organization_id),
        FilterExpression=Key('id').eq(member_id)
    )

    items = response.get('Items', [])
    if items:
        member_uuid = items[0]['memberUuid']
        members_table.delete_item(Key={'memberUuid': member_uuid})

def handle_push_subscription(event):
    try:
        body = json.loads(event['body'])
        fcm_token = body['fcmToken']
        organization_id = body['organizationId']
        admin_id = body['adminId']

        logger.info(f"Handling push subscription for organization {organization_id}, admin {admin_id}")

        # 既存のトークンを取得
        existing_endpoint_arn = get_existing_subscription(organization_id, admin_id)
        if existing_endpoint_arn:
            existing_token = get_token_from_endpoint(existing_endpoint_arn)
            if existing_token == fcm_token:
                logger.info(f"Token for admin {admin_id} in organization {organization_id} is already up to date")
                return create_response(200, {'message': 'Token is already up to date', 'endpointArn': existing_endpoint_arn})

        endpoint_arn = create_sns_endpoint(fcm_token, organization_id, admin_id)
        logger.info(f"Created SNS endpoint: {endpoint_arn}")

        update_result = update_organization_subscription(organization_id, admin_id, endpoint_arn)
        logger.info(f"Update result: {update_result}")

        return create_response(200, {'message': 'Subscription saved successfully', 'endpointArn': endpoint_arn})
    except ValueError as e:
        logger.error(f"Invalid request data: {str(e)}")
        return create_response(400, {'message': f"Invalid request data: {str(e)}"})
    except ClientError as e:
        logger.error(f"AWS service error: {str(e)}")
        return create_response(500, {'message': f"AWS service error: {str(e)}"})
    except Exception as e:
        logger.error(f"Unexpected error in handle_push_subscription: {str(e)}", exc_info=True)
        return create_response(500, {'message': f"Internal server error: {str(e)}"})

def get_token_from_endpoint(endpoint_arn):
    try:
        response = sns_client.get_endpoint_attributes(
            EndpointArn=endpoint_arn
        )
        return response['Attributes'].get('Token')
    except ClientError as e:
        logger.error(f"Failed to get token from endpoint: {str(e)}")
        return None

def create_sns_endpoint(fcm_token, organization_id, admin_id):
    try:
        response = sns_client.create_platform_endpoint(
            PlatformApplicationArn=WEB_PUSH_PLATFORM_ARN,
            Token=fcm_token,
            CustomUserData=json.dumps({
                'organizationId': organization_id,
                'adminId': admin_id
            })
        )
        return response['EndpointArn']
    except ClientError as e:
        logger.error(f"Failed to create SNS endpoint: {str(e)}")
        raise

def update_organization_subscription(organization_id, admin_id, endpoint_arn):
    try:
        # まず、adminSubscriptions 属性が存在するか確認
        response = organizations_table.update_item(
            Key={'organizationId': organization_id},
            UpdateExpression="SET adminSubscriptions.#adminId = :endpoint",
            ConditionExpression="attribute_exists(adminSubscriptions)",
            ExpressionAttributeNames={'#adminId': admin_id},
            ExpressionAttributeValues={':endpoint': endpoint_arn},
            ReturnValues="UPDATED_NEW"
        )
        logger.info(f"Successfully updated subscription for organization {organization_id}, admin {admin_id}")
        return response
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            # adminSubscriptions 属性が存在しない場合、新しく作成
            try:
                response = organizations_table.update_item(
                    Key={'organizationId': organization_id},
                    UpdateExpression="SET adminSubscriptions = :subscriptions",
                    ExpressionAttributeValues={
                        ':subscriptions': {admin_id: endpoint_arn}
                    },
                    ReturnValues="UPDATED_NEW"
                )
                logger.info(f"Created new adminSubscriptions for organization {organization_id}, admin {admin_id}")
                return response
            except ClientError as inner_e:
                logger.error(f"Failed to create adminSubscriptions: {str(inner_e)}")
                raise
        else:
            logger.error(f"Failed to update organization subscription: {str(e)}")
            raise

def handle_remove_subscription(event):
    try:
        params = event.get('queryStringParameters', {}) or {}
        organization_id = params.get('organizationId')
        admin_id = params.get('adminId')

        if not organization_id or not admin_id:
            return create_response(400, {'message': 'Missing required parameters: organizationId or adminId'})

        result = remove_organization_subscription(organization_id, admin_id)

        if result is None:
            return create_response(200, {'message': 'Subscription was already removed or did not exist'})
        else:
            return create_response(200, {'message': 'Subscription removed successfully'})
    except ClientError as e:
        logger.error(f"AWS service error: {str(e)}")
        return create_response(500, {'message': 'Failed to remove subscription'})
    except Exception as e:
        logger.error(f"Unexpected error in handle_remove_subscription: {str(e)}", exc_info=True)
        return create_response(500, {'message': 'Internal server error'})

def remove_organization_subscription(organization_id, admin_id):
    try:
        response = organizations_table.update_item(
            Key={'organizationId': organization_id},
            UpdateExpression="REMOVE adminSubscriptions.#adminId",
            ConditionExpression="attribute_exists(adminSubscriptions) AND attribute_exists(adminSubscriptions.#adminId)",
            ExpressionAttributeNames={'#adminId': admin_id},
            ReturnValues="UPDATED_OLD"
        )
        logger.info(f"Successfully removed subscription for organization {organization_id}, admin {admin_id}")
        return response
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            logger.warning(f"Subscription not found for organization {organization_id}, admin {admin_id}")
            return None
        else:
            logger.error(f"Failed to remove organization subscription: {str(e)}")
            raise
