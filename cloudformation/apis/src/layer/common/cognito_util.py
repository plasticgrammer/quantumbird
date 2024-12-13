import boto3
from botocore.exceptions import ClientError
from .exception import ApplicationException

def admin_create_user(user_pool_id, email, organization_id, organization_name, parent_organization_id=None, cognito_client=None):
    if cognito_client is None:
        cognito_client = boto3.client('cognito-idp')
        
    try:
        user_attributes = [
            {
                'Name': 'email',
                'Value': email
            },
            {
                'Name': 'custom:organizationId',
                'Value': organization_id
            },
            {
                'Name': 'email_verified',
                'Value': 'true'
            }
        ]

        if parent_organization_id:
            user_attributes.append({
                'Name': 'custom:parentOrganizationId',
                'Value': parent_organization_id
            })

        response = cognito_client.admin_create_user(
            UserPoolId=user_pool_id,
            Username=email,
            UserAttributes=user_attributes
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

def list_users(user_pool_id, cognito_client=None, parent_organization_id=None):
    if cognito_client is None:
        cognito_client = boto3.client('cognito-idp')
        
    try:
        response = cognito_client.list_users(
            UserPoolId=user_pool_id
        )
        users = []
        for user in response['Users']:
            user_attrs = {attr['Name']: attr['Value'] for attr in user['Attributes']}
            
            # カスタム属性の取得
            parent_org_id = user_attrs.get('custom:parentOrganizationId')
            org_id = user_attrs.get('custom:organizationId')
            
            # 親組織IDが指定されている場合のフィルタリング
            if parent_organization_id:
                if not parent_org_id or parent_org_id != parent_organization_id:
                    continue

            # 組織名はDynamoDBから取得
            org_name = None
            if org_id:
                try:
                    org = get_organization(org_id)
                    if org:
                        org_name = org.get('name')
                except:
                    pass

            users.append({
                'username': user['Username'],
                'status': user['UserStatus'],
                'organizationId': org_id,
                'organizationName': org_name,
                'email': user_attrs.get('email', ''),
                'parentOrganizationId': parent_org_id,
                'created': user['UserCreateDate'].isoformat()
            })
        return users
    except ClientError as e:
        raise ApplicationException(500, str(e))

def admin_get_user(user_pool_id, email, cognito_client=None):
    if cognito_client is None:
        cognito_client = boto3.client('cognito-idp')
        
    try:
        response = cognito_client.list_users(
            UserPoolId=user_pool_id,
            Filter=f'email = "{email}"'
        )
        users = response.get('Users', [])
        if not users:
            return None
        user = users[0]
        user_attrs = {attr['Name']: attr['Value'] for attr in user['Attributes']}
        return {
            'username': user['Username'],
            'status': user['UserStatus'],
            'organizationId': user_attrs.get('custom:organizationId'),
            'parentOrganizationId': user_attrs.get('custom:parentOrganizationId'),
            'email': user_attrs.get('email', ''),
            'created': user['UserCreateDate'].isoformat()
        }
    except ClientError as e:
        raise ApplicationException(500, str(e))