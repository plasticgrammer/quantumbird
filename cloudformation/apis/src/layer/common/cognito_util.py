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

def get_admin_emails(user_pool_id, organization_id, cognito_client=None):
    """
    組織の管理者のメールアドレスを取得
    
    Args:
        user_pool_id (str): Cognito User Pool ID
        organization_id (str): 組織ID
        cognito_client: boto3 cognito clientのインスタンス（オプション）
    
    Returns:
        list: 管理者のメールアドレスのリスト
    """
    if cognito_client is None:
        cognito_client = boto3.client('cognito-idp')
        
    try:
        admin_emails = set()
        pagination_token = None
        
        while True:
            kwargs = {
                'UserPoolId': user_pool_id,
                'AttributesToGet': ['email', 'custom:organizationId']
            }
            if pagination_token:
                kwargs['PaginationToken'] = pagination_token
            
            response = cognito_client.list_users(**kwargs)
            
            for user in response.get('Users', []):
                is_org_member = False
                email = None
                
                for attr in user.get('Attributes', []):
                    if attr['Name'] == 'custom:organizationId' and attr['Value'] == organization_id:
                        is_org_member = True
                    elif attr['Name'] == 'email':
                        email = attr['Value']
                    
                    if is_org_member and email:
                        admin_emails.add(email)
                        break
            
            pagination_token = response.get('PaginationToken')
            if not pagination_token:
                break

        return list(admin_emails)
    except Exception as e:
        raise ApplicationException(500, f"Error getting admin emails: {str(e)}")

def get_organization_admin_subs(user_pool_id, organization_id, cognito_client=None):
    """
    組織の管理者のsub属性を取得
    
    Args:
        user_pool_id (str): Cognito User Pool ID
        organization_id (str): 組織ID
        cognito_client: boto3 cognito clientのインスタンス（オプション）
    
    Returns:
        list: 管理者のsubのリスト
    """
    if cognito_client is None:
        cognito_client = boto3.client('cognito-idp')
        
    try:
        admin_subs = set()
        pagination_token = None
        
        while True:
            kwargs = {
                'UserPoolId': user_pool_id,
                'Filter': f'custom:organizationId = "{organization_id}"'
            }
            if pagination_token:
                kwargs['PaginationToken'] = pagination_token
            
            response = cognito_client.list_users(**kwargs)
            
            for user in response.get('Users', []):
                sub = next((attr['Value'] for attr in user.get('Attributes', [])
                          if attr['Name'] == 'sub'), None)
                if sub:
                    admin_subs.add(sub)
            
            pagination_token = response.get('PaginationToken')
            if not pagination_token:
                break

        return list(admin_subs)
    except Exception as e:
        raise ApplicationException(500, f"Error getting admin subs: {str(e)}")