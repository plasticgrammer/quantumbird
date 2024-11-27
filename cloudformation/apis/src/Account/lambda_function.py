import json
import os
import boto3
from botocore.exceptions import ClientError
from common.utils import create_response
from common.exception import ApplicationException
from common.cognito_util import admin_create_user, admin_delete_user, list_users, admin_get_user

USER_POOL_ID = os.environ.get('USER_POOL_ID')
USER_POOL_REGION = os.environ.get('USER_POOL_REGION')  # デフォルト値を削除
cognito = boto3.client('cognito-idp', region_name=USER_POOL_REGION)

def lambda_handler(event, context):
    try:
        http_method = event['httpMethod']
        
        if http_method == 'POST':
            # アカウント作成
            body = json.loads(event['body'])
            result = admin_create_user(
                user_pool_id=USER_POOL_ID,
                email=body['email'],
                organization_id=body['organizationId'],
                organization_name=body['organizationName'],
                cognito_client=cognito
            )
            return create_response(200, result)
            
        elif http_method == 'GET':
            # アカウント一覧取得 or 単一アカウント取得
            query_params = event.get('queryStringParameters', {}) or {}
            organization_id = query_params.get('organizationId')
            
            if organization_id:
                # 単一アカウント取得
                result = admin_get_user(
                    user_pool_id=USER_POOL_ID,
                    organization_id=organization_id,
                    cognito_client=cognito
                )
            else:
                # アカウント一覧取得
                result = list_users(USER_POOL_ID, cognito_client=cognito)
            return create_response(200, result)
            
        elif http_method == 'DELETE':
            # アカウント削除
            query_params = event.get('queryStringParameters', {}) or {}
            organization_id = query_params.get('organizationId')
            if not organization_id:
                raise ApplicationException(400, 'organizationId is required')
                
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