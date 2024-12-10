import json
import os
import boto3
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
            Username=email,  # メールアドレスをUsernameとして使用
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

def update_user_attributes(user_pool_id, organization_id, email, cognito_client):
    """Cognitoユーザーの属性を更新する"""
    try:
        # まずユーザーを検索
        try:
            # organizationIdで直接ユーザーを取得（Usernameとして使用）
            user = cognito_client.admin_get_user(
                UserPoolId=user_pool_id,
                Username=organization_id
            )
            if not user:
                raise ApplicationException(404, f'ユーザーが見つかりません: {organization_id}')
        except ClientError as e:
            if e.response['Error']['Code'] == 'UserNotFoundException':
                raise ApplicationException(404, f'ユーザーが見つかりません: {organization_id}')
            raise ApplicationException(500, f"ユーザー検索に失敗しました: {str(e)}")

        # ユーザー属性を更新
        user_attributes = [
            {'Name': 'email', 'Value': email}
        ]
        
        cognito_client.admin_update_user_attributes(
            UserPoolId=user_pool_id,
            Username=organization_id,  # 組織IDをユーザー名として使用
            UserAttributes=user_attributes
        )
    except ApplicationException as e:
        raise e
    except ClientError as e:
        raise ApplicationException(500, f"ユーザー情報の更新に失敗しました: {str(e)}")

def lambda_handler(event, context):
    try:
        path = event.get('path', '')
        http_method = event['httpMethod']
        
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

            # メールアドレスからユーザーを検索（修正）
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
                
            # Cognitoユーザーを作成
            result = admin_create_user(
                user_pool_id=USER_POOL_ID,
                email=body['email'],
                organization_id=body['organizationId'],
                organization_name=body['organizationName'],
                parent_organization_id=body['parentOrganizationId'],
                cognito_client=cognito
            )

            # 作成した組織情報を取得して結果に含める
            organization = get_organization(body['organizationId'])
            if organization:
                result['organization'] = organization

            return create_response(200, result)
            
        elif http_method == 'PUT':
            body = json.loads(event['body'])
            organization_id = body.get('organizationId')
            if not organization_id:
                raise ApplicationException(400, 'organizationId is required')

            # 更新対象が自分の子アカウントであることを確認
            target_user = admin_get_user(USER_POOL_ID, organization_id, cognito)
            if target_user.get('parentOrganizationId') != requester_organization_id:
                raise ApplicationException(403, '権限がありません')

            try:
                # 組織情報を更新
                update_organization(organization_id, body['organizationName'])
                
                # Cognitoユーザー情報を更新
                update_user_attributes(
                    user_pool_id=USER_POOL_ID,
                    organization_id=organization_id,
                    email=body['email'],
                    cognito_client=cognito
                )

                return create_response(200, {
                    'message': 'アカウント情報を更新しました',
                    'organizationId': organization_id
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
            if not organization_id:
                raise ApplicationException(400, 'organizationId is required')
                
            # 削除対象が自分の子アカウントであることを確認
            target_user = admin_get_user(USER_POOL_ID, organization_id, cognito)
            if target_user.get('parentOrganizationId') != requester_organization_id:
                raise ApplicationException(403, '権限がありません')
                
            # 削除処理を実行
            admin_delete_user(
                user_pool_id=USER_POOL_ID,
                organization_id=organization_id,
                cognito_client=cognito
            )
            
            # 正しいレスポンス形式を返す
            return create_response(200, {'message': 'アカウントを削除しました', 'organizationId': organization_id})
            
        else:
            return create_response(405, {'message': 'Method not allowed'})
            
    except ApplicationException as e:
        return create_response(e.status_code, {'message': str(e)})
    except Exception as e:
        return create_response(500, {'message': str(e)})