import json
import os
import boto3
import logging
from botocore.exceptions import ClientError
from common.utils import create_response
from common.exception import ApplicationException
from common.cognito_util import admin_create_user, admin_delete_user, list_users, admin_get_user
import common.dynamo_items as dynamo_items

USER_POOL_ID = os.environ.get('USER_POOL_ID')
USER_POOL_REGION = os.environ.get('USER_POOL_REGION')
cognito = boto3.client('cognito-idp', region_name=USER_POOL_REGION)

dynamodb = boto3.resource('dynamodb')
organizations_table_name = f'{os.environ.get("STAGE", "dev")}-Organizations'
organizations_table = dynamodb.Table(organizations_table_name)

# ロガーの設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_organization(organization_id):
    try:
        response = organizations_table.get_item(
            Key={'organizationId': organization_id}
        )
        item = response.get('Item')
        if item:
            # nameフィールドが存在しない場合、organizationNameを使用
            if 'name' not in item and 'organizationName' in item:
                item['name'] = item['organizationName']
        return item
    except Exception as e:
        raise ApplicationException(500, f"組織情報の取得に失敗しました: {str(e)}")

def create_organization(organization_data):
    try:
        item = dynamo_items.prepare_organization_item(organization_data)
        organizations_table.put_item(Item=item)
    except Exception as e:
        raise ApplicationException(500, f"組織の作成に失敗しました: {str(e)}")

def check_organization_exists(organization_id):
    """組織IDが既に存在するかチェック"""
    try:
        org = organizations_table.get_item(
            Key={'organizationId': organization_id}
        )
        return 'Item' in org
    except Exception as e:
        raise ApplicationException(500, f"組織情報の確認に失敗しました: {str(e)}")

def enrich_user_with_organization(user):
    """ユーザー情報に組織情報を追加"""
    if 'organizationId' in user:
        org = get_organization(user['organizationId'])
        if org:
            # nameフィールドまたはorganizationNameフィールドを使用
            user['organizationName'] = org.get('name') or org.get('organizationName')
    return user

def resend_invitation(user_pool_id, organization_id, email, cognito_client):
    """招待メールを再送信する"""
    try:
        response = cognito_client.admin_create_user(
            UserPoolId=user_pool_id,
            Username=email,
            MessageAction='RESEND'
        )
        return response['User']
    except ClientError as e:
        if e.response['Error']['Code'] == 'UserNotFoundException':
            raise ApplicationException(404, 'ユーザーが見つかりません')
        raise ApplicationException(500, f"招待メールの再送信に失敗しました: {str(e)}")

def update_organization(organization_id, organization_name):
    """組織名を更新する"""
    try:
        organizations_table.update_item(
            Key={'organizationId': organization_id},
            UpdateExpression='SET #name = :name, organizationName = :name',
            ExpressionAttributeNames={'#name': 'name'},
            ExpressionAttributeValues={':name': organization_name}
        )
    except Exception as e:
        raise ApplicationException(500, f"組織情報の更新に失敗しました: {str(e)}")

def update_user_attributes(user_pool_id, organization_id, old_email, new_email, cognito_client):
    """Cognitoユーザーの属性を更新する"""
    try:
        # メールアドレスでユーザーを検索
        response = cognito_client.list_users(
            UserPoolId=user_pool_id,
            Filter=f'email = "{old_email}"'
        )
        users = response.get('Users', [])
        if not users:
            raise ApplicationException(404, 'ユーザーが見つかりません')

        user = users[0]
        username = user['Username']
        
        # メールアドレスが変更されている場合のみ更新
        if old_email != new_email:
            # メールアドレス属性を更新
            user_attributes = [
                {'Name': 'email', 'Value': new_email},
                {'Name': 'email_verified', 'Value': 'true'}
            ]
            
            cognito_client.admin_update_user_attributes(
                UserPoolId=user_pool_id,
                Username=username,
                UserAttributes=user_attributes
            )
            
            # 招待メールを送信
            cognito_client.admin_create_user(
                UserPoolId=user_pool_id,
                Username=new_email,
                MessageAction='RESEND',
                UserAttributes=user_attributes
            )

    except ClientError as e:
        raise ApplicationException(500, f"ユーザー情報の更新に失敗しました: {str(e)}")

def lambda_handler(event, context):
    try:
        path = event.get('path', '')
        http_method = event['httpMethod']
        
        # リクエスト情報をログ出力
        #logger.info(f"Request: {http_method} {path}")
        #logger.info(f"Event: {json.dumps(event)}")
        
        # Cognitoの認証情報から組織IDを取得
        requester_claims = event.get('requestContext', {}).get('authorizer', {}).get('claims', {})
        requester_organization_id = requester_claims.get('custom:organizationId')
        if not requester_organization_id:
            raise ApplicationException(401, '組織IDが必要です')

        # 招待メール再送信用のエンドポイント
        if path.endswith('/resend-invitation'):
            if http_method != 'POST':  # POSTメソッドのみ許可
                return create_response(405, {'message': 'Method not allowed'})
                
            body = json.loads(event.get('body', '{}'))
            email = body.get('email')
            if not email:
                raise ApplicationException(400, 'email is required')

            # メールアドレスからユーザーを検索
            try:
                response = cognito.list_users(
                    UserPoolId=USER_POOL_ID,
                    Filter=f'email = "{email}"'
                )
                target_users = response.get('Users', [])
            except Exception as e:
                raise ApplicationException(500, f"ユーザー検索に失敗しました: {str(e)}")
            
            if not target_users:
                raise ApplicationException(404, 'ユーザーが見つかりません')
            
            target_user = target_users[0]  # 最初のユーザーを使用
            
            # ユーザー属性から必要な情報を取得
            user_email = email  # 入力されたメールアドレスを使用
            organization_id = None
            for attr in target_user.get('Attributes', []):
                if attr['Name'] == 'custom:organizationId':
                    organization_id = attr['Value']
                    break
            
            if not organization_id:
                raise ApplicationException(500, 'ユーザーの組織IDが見つかりません')
            
            result = resend_invitation(
                user_pool_id=USER_POOL_ID,
                organization_id=organization_id,
                email=user_email,  # メールアドレスを追加
                cognito_client=cognito
            )

            return create_response(200, {
                'message': '招待メールを再送信しました',
                'email': email,
                'organizationId': organization_id
            })

        # 既存のエンドポイント処理
        if http_method == 'POST':
            body = json.loads(event['body'])
            # 親組織IDが自分の組織IDと一致することを確認
            if body.get('parentOrganizationId') != requester_organization_id:
                raise ApplicationException(403, '権限がありません')

            # 組織IDの重複チェック
            if check_organization_exists(body['organizationId']):
                raise ApplicationException(409, '指定された組織IDは既に使用されています')
                
            # Cognitoユーザーを作成
            result = admin_create_user(
                user_pool_id=USER_POOL_ID,
                email=body['email'],
                organization_id=body['organizationId'],
                organization_name=body['organizationName'],
                parent_organization_id=body['parentOrganizationId'],
                cognito_client=cognito
            )
            # 組織を作成
            org_data = {
                'organizationId': body['organizationId'],
                'name': body['organizationName'],
                'parentOrganizationId': body['parentOrganizationId'],
                'sender': 'notify@fluxweek.com',
                'senderName': body['organizationName'],
                'features': { 'weeklyReportAdvice': True, 'advisors': ['manager', 'career', 'mental'] }
            }
            create_organization(org_data)

            # 作成した組織情報を取得して結果に含める
            organization = get_organization(body['organizationId'])
            if organization:
                result['organization'] = organization

            return create_response(200, result)
            
        elif http_method == 'PUT':
            body = json.loads(event['body'])
            organization_id = body.get('organizationId')
            old_email = body.get('oldEmail')
            new_email = body.get('email')
            organization_name = body.get('organizationName')

            if not organization_id or not old_email or not new_email:
                raise ApplicationException(400, 'organizationId, oldEmail, email は必須です')
            
            # ユーザーの存在確認と権限チェック
            target_user = admin_get_user(USER_POOL_ID, old_email, cognito)
            if not target_user:
                raise ApplicationException(404, 'ユーザーが見つかりません')
            
            if target_user.get('parentOrganizationId') != requester_organization_id and target_user.get('organizationId') != requester_organization_id:
                raise ApplicationException(403, '権限がありません')

            try:
                # 組織名の更新
                if organization_name:
                    update_organization(organization_id, organization_name)

                # ユーザー属性の更新とメール送信
                update_user_attributes(
                    user_pool_id=USER_POOL_ID,
                    organization_id=organization_id,
                    old_email=old_email,
                    new_email=new_email,
                    cognito_client=cognito
                )

                return create_response(200, {
                    'message': 'アカウント情報を更新し、招待メールを送信しました',
                    'organizationId': organization_id,
                    'email': new_email
                })
            except ApplicationException as e:
                raise e
            except Exception as e:
                raise ApplicationException(500, f"アカウント情報の更新に失敗しました: {str(e)}")
            
        elif http_method == 'GET':
            params = event.get('queryStringParameters', {}) or {}
            organization_id = params.get('organizationId')
            
            # 単一アカウント取得時は親組織IDチェックを行う
            if organization_id:
                result = admin_get_user(USER_POOL_ID, organization_id, cognito)
                if result and result.get('parentOrganizationId') != requester_organization_id:
                    raise ApplicationException(403, '権限がありません')
                # 組織情報を付加
                result = enrich_user_with_organization(result)
            else:
                # アカウント一覧取得時
                result = list_users(
                    USER_POOL_ID,
                    cognito_client=cognito,
                    parent_organization_id=requester_organization_id
                )
                # 各ユーザーに組織情報を付加
                enriched_results = []
                for user in result:
                    enriched_user = enrich_user_with_organization(user)
                    if enriched_user:
                        enriched_results.append(enriched_user)
                result = enriched_results

            return create_response(200, result)
            
        elif http_method == 'DELETE':
            params = event.get('queryStringParameters', {}) or {}
            organization_id = params.get('organizationId')
            email = params.get('email')
            
            if not organization_id or not email:
                raise ApplicationException(400, 'organizationId and email are required')
                
            logger.info(f"Deleting account for organization: {organization_id}, email: {email}")
            
            # 削除対象が自分の子アカウントであることを確認
            target_user = admin_get_user(USER_POOL_ID, email, cognito)
            if not target_user:
                logger.info(f"User not found for email: {email}")
                # 削除済みとして扱う
                return create_response(200, {'message': f"User not found for email: {email}"})
                
            elif target_user.get('parentOrganizationId') != requester_organization_id:
                logger.error(f"Permission denied. Requester: {requester_organization_id}, Target parent: {target_user.get('parentOrganizationId')}")
                raise ApplicationException(403, '権限がありません')

            else: 
                # 削除処理を実行
                try:
                    result = admin_delete_user(
                        user_pool_id=USER_POOL_ID,
                        email=email,
                        cognito_client=cognito
                    )
                    logger.info(f"Successfully deleted account: {organization_id}, email: {email}")
                    return create_response(200, result)
                except ApplicationException as e:
                    logger.error(f"Failed to delete account: {str(e)}")
                    raise
                except Exception as e:
                    logger.error(f"Unexpected error while deleting account: {str(e)}")
                    raise ApplicationException(500, f"アカウントの削除に失敗しました: {str(e)}")
        
        else:
            return create_response(405, {'message': 'Method not allowed'})
            
    except ApplicationException as e:
        logger.error(f"Application error: {str(e)}")
        return create_response(e.status_code, {'message': str(e)})
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return create_response(500, {'message': str(e)})