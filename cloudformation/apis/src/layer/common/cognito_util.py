import boto3
from botocore.exceptions import ClientError
from .exception import ApplicationException

def admin_create_user(user_pool_id, email, organization_id, organization_name, cognito_client=None):
    if cognito_client is None:
        cognito_client = boto3.client('cognito-idp')
        
    try:
        response = cognito_client.admin_create_user(
            UserPoolId=user_pool_id,
            Username=email,
            UserAttributes=[
                {
                    'Name': 'email',
                    'Value': email
                },
                {
                    'Name': 'custom:organization_id',
                    'Value': organization_id
                },
                {
                    'Name': 'custom:organization_name',
                    'Value': organization_name
                },
                {
                    'Name': 'email_verified',
                    'Value': 'true'
                }
            ],
            MessageAction='SUPPRESS'
        )
        return {
            'username': response['User']['Username'],
            'status': response['User']['UserStatus'],
            'created': response['User']['UserCreateDate'].isoformat()
        }
    except ClientError as e:
        if e.response['Error']['Code'] == 'UsernameExistsException':
            raise ApplicationException(409, 'ユーザーは既に存在します')
        raise ApplicationException(500, str(e))

def admin_delete_user(user_pool_id, organization_id, cognito_client=None):
    if cognito_client is None:
        cognito_client = boto3.client('cognito-idp')
        
    try:
        # 組織IDからユーザーを検索
        user = admin_get_user(user_pool_id, organization_id, cognito_client)
        if not user:
            raise ApplicationException(404, 'ユーザーが見つかりません')
            
        cognito_client.admin_delete_user(
            UserPoolId=user_pool_id,
            Username=user['username']
        )
        return {'message': 'ユーザーを削除しました'}
    except ClientError as e:
        raise ApplicationException(500, str(e))

def list_users(user_pool_id, cognito_client=None):
    if cognito_client is None:
        cognito_client = boto3.client('cognito-idp')
        
    try:
        response = cognito_client.list_users(
            UserPoolId=user_pool_id
        )
        users = []
        for user in response['Users']:
            user_attrs = {attr['Name']: attr['Value'] for attr in user['Attributes']}
            users.append({
                'username': user['Username'],
                'status': user['UserStatus'],
                'organizationId': user_attrs.get('custom:organization_id', ''),
                'organizationName': user_attrs.get('custom:organization_name', ''),
                'email': user_attrs.get('email', ''),
                'created': user['UserCreateDate'].isoformat()
            })
        return users
    except ClientError as e:
        raise ApplicationException(500, str(e))

def admin_get_user(user_pool_id, organization_id, cognito_client=None):
    if cognito_client is None:
        cognito_client = boto3.client('cognito-idp')
        
    try:
        users = list_users(user_pool_id, cognito_client)
        for user in users:
            if user['organizationId'] == organization_id:
                return user
        return None
    except ClientError as e:
        raise ApplicationException(500, str(e))