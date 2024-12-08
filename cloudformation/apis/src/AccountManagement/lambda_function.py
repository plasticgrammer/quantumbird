import json
import os
import re
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
        return response.get('Item')
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

def validate_organization_id(organization_id):
    """組織IDのバリデーション"""
    if not organization_id:
        raise ApplicationException(400, '組織IDは必須です')
    if len(organization_id) < 3:
        raise ApplicationException(400, '組織IDは3文字以上で入力してください')
    if len(organization_id) > 20:
        raise ApplicationException(400, '組織IDは20文字以下で入力してください')
    if not re.match(r'^[a-zA-Z0-9_-]+$', organization_id):
        raise ApplicationException(400, '組織IDは英数字、ハイフン、アンダースコアのみで入力してください')

def lambda_handler(event, context):
    try:
        http_method = event['httpMethod']
        # Cognitoの認証情報から組織IDを取得
        requester_claims = event.get('requestContext', {}).get('authorizer', {}).get('claims', {})
        requester_organization_id = requester_claims.get('custom:organizationId')

        if not requester_organization_id:
            raise ApplicationException(401, '組織IDが取得できません')

        if http_method == 'POST':
            body = json.loads(event['body'])
            # 組織IDの検証を追加
            validate_organization_id(body['organizationId'])
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
                'parentOrganizationId': body['parentOrganizationId']
            }
            create_organization(org_data)
                
            result = admin_create_user(
                user_pool_id=USER_POOL_ID,
                email=body['email'],
                organization_id=body['organizationId'],
                organization_name=body['organizationName'],
                parent_organization_id=body['parentOrganizationId'],
                cognito_client=cognito
            )
            return create_response(200, result)
            
        elif http_method == 'GET':
            params = event.get('queryStringParameters', {}) or {}
            organization_id = params.get('organizationId')
            
            # 単一アカウント取得時は親組織IDチェックを行う
            if organization_id:
                result = admin_get_user(USER_POOL_ID, organization_id, cognito)
                # 取得したユーザーが自分の子アカウントであることを確認
                if result and result.get('parentOrganizationId') != requester_organization_id:
                    raise ApplicationException(403, '権限がありません')
            else:
                # 親組織IDが自分の組織IDと一致することを確認
                if params.get('parentOrganizationId') != requester_organization_id:
                    raise ApplicationException(403, '権限がありません')
                # アカウント一覧取得時は親組織IDでフィルタリング
                result = list_users(
                    USER_POOL_ID,
                    cognito_client=cognito,
                    parent_organization_id=requester_organization_id  # 常にリクエスト元の組織IDを使用
                )
            return create_response(200, result)
            
        elif http_method == 'DELETE':
            # ボディからパラメータを取得するように変更
            body = json.loads(event.get('body', '{}'))
            organization_id = body.get('organizationId')
            if not organization_id:
                raise ApplicationException(400, 'organizationId is required')
                
            # 削除対象が自分の子アカウントであることを確認
            target_user = admin_get_user(USER_POOL_ID, organization_id, cognito)
            if target_user.get('parentOrganizationId') != requester_organization_id:
                raise ApplicationException(403, '権限がありません')
                
            result = admin_delete_user(
                user_pool_id=USER_POOL_ID,
                organization_id=organization_id,
                cognito_client=cognito
            )
            return create_response(200, result)
            
        else:
            return create_response(405, {'message': 'Method not allowed'})
            
    except ApplicationException as e:
        return create_response(e.status_code, {'message': str(e)})
    except Exception as e:
        return create_response(500, {'message': str(e)})