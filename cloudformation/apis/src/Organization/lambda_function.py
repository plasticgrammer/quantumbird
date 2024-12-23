import json
import logging
import boto3
import os
import common.dynamo_items as dynamo_items
import common.cognito_util as cognito_util
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
            ProjectionExpression='features.notifySubscriptions'
        )
        admin_subscriptions = response.get('Item', {}).get('features', {}).get('notifySubscriptions', {})
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
        return create_response(200, org)
    else:
        orgs = list_organizations()
        return create_response(200, orgs)

def handle_post(event):
    data = json.loads(event['body'])
    if 'organizationId' in data:
        item = dynamo_items.prepare_organization_item(data)
        response = organizations_table.put_item(Item=item)
        return create_response(201, {'message': 'Organization created successfully'})
    else:
        return create_response(400, {'message': 'Invalid data structure'})

def handle_put(event):
    data = json.loads(event['body'])
    if 'organizationId' in data:
        existing_org = get_organization(data['organizationId'])
        
        if existing_org is None:
            existing_org = {}
            
        org_item = dynamo_items.prepare_organization_item(data, existing_org)
        organizations_table.put_item(Item=org_item)
        return create_response(200, {'message': 'Organization updated successfully'})
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
        # 1. プッシュ通知登録の削除
        delete_push_subscriptions(organization_id)
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
        # 1. プッシュ通知登録の削除
        delete_push_subscriptions(organization_id)
        # 2. 週次報告データの削除
        delete_weekly_reports(organization_id)
        # 3. ユーザータスクの削除
        delete_user_tasks(organization_id)
        # 4. メンバーデータの削除
        delete_members_by_organization(organization_id)
        # 5. 組織データの削除
        organizations_table.delete_item(
            Key={
                'organizationId': organization_id
            }
        )
        logger.info(f"Deleted organization data completely for: {organization_id}")

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
        user_pool_id = os.environ['USER_POOL_ID']
        user_pool_region = os.environ['USER_POOL_REGION']
        
        # Cognitoクライアントを正しいリージョンで初期化
        cognito_client = boto3.client('cognito-idp', region_name=user_pool_region)
        admin_subs = cognito_util.get_organization_admin_subs(user_pool_id, organization_id, cognito_client)

        if not admin_subs:
            logger.warning(f"No admin users found for organization: {organization_id}")
            return 0

        total_deleted = 0
        for user_id in admin_subs:
            last_evaluated_key = None
            while True:
                query_params = {
                    'KeyConditionExpression': Key('userId').eq(user_id)
                }
                if last_evaluated_key:
                    query_params['ExclusiveStartKey'] = last_evaluated_key

                response = user_tasks_table.query(**query_params)
                items = response.get('Items', [])

                if not items:
                    break

                with user_tasks_table.batch_writer() as batch:
                    for item in items:
                        batch.delete_item(
                            Key={
                                'userId': item['userId'],
                                'taskId': item['taskId']
                            }
                        )
                        total_deleted += 1

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
        if not org or 'features' not in org or 'notifySubscriptions' not in org['features']:
            return 0

        admin_subscriptions = org['features'].get('notifySubscriptions', {})
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

def handle_push_subscription(event):
    try:
        body = json.loads(event['body'])
        fcm_token = body['fcmToken']
        organization_id = body['organizationId']
        admin_id = body['adminId']

        logger.info(f"Handling push subscription for organization {organization_id}, admin {admin_id}")

        # 既存のトークンを確認と必要に応じて削除
        existing_endpoint_arn = get_existing_subscription(organization_id, admin_id)
        if existing_endpoint_arn:
            try:
                existing_token = get_token_from_endpoint(existing_endpoint_arn)
                if existing_token == fcm_token:
                    # 既存のトークンが同じ場合は有効性を確認
                    if check_endpoint_validity(existing_endpoint_arn):
                        logger.info(f"Token for admin {admin_id} is already up to date and valid")
                        return create_response(200, {
                            'message': 'Token is already up to date',
                            'endpointArn': existing_endpoint_arn
                        })
                # 既存のエンドポイントを削除
                delete_sns_endpoint(existing_endpoint_arn)
            except Exception as e:
                logger.warning(f"Error handling existing endpoint: {str(e)}")
                # エラーが発生しても続行（新しいエンドポイントを作成）

        # トランザクション的な処理
        try:
            # 新しいSNSエンドポイントを作成
            endpoint_arn = create_sns_endpoint(fcm_token, organization_id, admin_id)
            logger.info(f"Created SNS endpoint: {endpoint_arn}")
            # DynamoDBを更新
            update_result = update_organization_subscription(organization_id, admin_id, endpoint_arn)

            return create_response(200, {
                'message': 'Subscription saved successfully',
                'endpointArn': endpoint_arn
            })
        except Exception as e:
            # エラーが発生した場合、作成したエンドポイントを削除
            if 'endpoint_arn' in locals():
                try:
                    delete_sns_endpoint(endpoint_arn)
                except Exception as cleanup_error:
                    logger.error(f"Failed to cleanup endpoint after error: {cleanup_error}")
            raise

    except Exception as e:
        logger.error(f"Unexpected error in handle_push_subscription: {str(e)}", exc_info=True)
        return create_response(500, {'message': f"Internal server error: {str(e)}"})

def check_endpoint_validity(endpoint_arn):
    """SNSエンドポイントの有効性を確認"""
    try:
        response = sns_client.get_endpoint_attributes(
            EndpointArn=endpoint_arn
        )
        return response['Attributes']['Enabled'] == 'true'
    except ClientError as e:
        logger.error(f"Failed to check endpoint validity: {str(e)}")
        return False

def delete_sns_endpoint(endpoint_arn):
    """SNSエンドポイントを削除"""
    try:
        sns_client.delete_endpoint(
            EndpointArn=endpoint_arn
        )
        logger.info(f"Successfully deleted SNS endpoint: {endpoint_arn}")
    except ClientError as e:
        logger.error(f"Failed to delete SNS endpoint: {str(e)}")
        raise

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
        # まず、features.notifySubscriptions 属性が存在するか確認
        response = organizations_table.update_item(
            Key={'organizationId': organization_id},
            UpdateExpression="SET features.notifySubscriptions.#adminId = :endpoint",
            ConditionExpression="attribute_exists(features.notifySubscriptions)",
            ExpressionAttributeNames={'#adminId': admin_id},
            ExpressionAttributeValues={':endpoint': endpoint_arn},
            ReturnValues="UPDATED_NEW"
        )
        logger.info(f"Successfully updated subscription for organization {organization_id}, admin {admin_id}")
        return response
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            # features.notifySubscriptions 属性が存在しない場合、新しく作成
            try:
                response = organizations_table.update_item(
                    Key={'organizationId': organization_id},
                    UpdateExpression="SET features.notifySubscriptions = :subscriptions",
                    ExpressionAttributeValues={
                        ':subscriptions': {admin_id: endpoint_arn}
                    },
                    ReturnValues="UPDATED_NEW"
                )
                logger.info(f"Created new features.notifySubscriptions for organization {organization_id}, admin {admin_id}")
                return response
            except ClientError as inner_e:
                logger.error(f"Failed to create features.notifySubscriptions: {str(inner_e)}")
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
            UpdateExpression="REMOVE features.notifySubscriptions.#adminId",
            ConditionExpression="attribute_exists(features.notifySubscriptions) AND attribute_exists(features.notifySubscriptions.#adminId)",
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
