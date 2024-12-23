import boto3
from botocore.exceptions import ClientError
from .exception import ApplicationException

def _get_cognito_client(cognito_client=None):
    return cognito_client if cognito_client else boto3.client('cognito-idp')

def _get_all_users(user_pool_id, cognito_client, attributes_to_get=None):
    """ページネーションを使用してすべてのユーザーを取得する共通関数"""
    users = []
    pagination_token = None
    
    while True:
        kwargs = {'UserPoolId': user_pool_id}
        if pagination_token:
            kwargs['PaginationToken'] = pagination_token
        if attributes_to_get:
            kwargs['AttributesToGet'] = attributes_to_get
            
        response = cognito_client.list_users(**kwargs)
        users.extend(response.get('Users', []))
        
        pagination_token = response.get('PaginationToken')
        if not pagination_token:
            break
            
    return users

def _get_user_attributes(user):
    """ユーザー属性をディクショナリとして取得する共通関数"""
    return {attr['Name']: attr['Value'] for attr in user.get('Attributes', [])}

def _filter_users_by_organization(users, organization_id, parent_organization_id=None):
    """組織IDでユーザーをフィルタリングする共通関数"""
    filtered_users = []
    
    for user in users:
        user_attrs = _get_user_attributes(user)
        org_id = user_attrs.get('custom:organizationId')
        parent_org_id = user_attrs.get('custom:parentOrganizationId')
        
        if organization_id and org_id != organization_id:
            continue
            
        if parent_organization_id and parent_org_id != parent_organization_id:
            continue
            
        filtered_users.append((user, user_attrs))
    
    return filtered_users

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

def admin_delete_user(user_pool_id, email, cognito_client=None):
    if cognito_client is None:
        cognito_client = boto3.client('cognito-idp')
        
    try:
        # メールアドレスからユーザーを検索
        response = cognito_client.list_users(
            UserPoolId=user_pool_id,
            Filter=f'email = "{email}"'
        )
        users = response.get('Users', [])
        if not users:
            raise ApplicationException(404, f'ユーザーが見つかりません: {email}')
            
        user = users[0]
        cognito_client.admin_delete_user(
            UserPoolId=user_pool_id,
            Username=user['Username']
        )
        return {
            'message': 'ユーザーを削除しました',
            'email': email,
            'username': user['Username']
        }
    except ClientError as e:
        if e.response['Error']['Code'] == 'UserNotFoundException':
            raise ApplicationException(404, f'ユーザーが見つかりません: {email}')
        raise ApplicationException(500, f"ユーザーの削除に失敗しました: {str(e)}")

def list_users(user_pool_id, cognito_client=None, parent_organization_id=None):
    cognito_client = _get_cognito_client(cognito_client)
    
    try:
        users = _get_all_users(user_pool_id, cognito_client)
        filtered_users = _filter_users_by_organization(users, None, parent_organization_id)
        
        result = []
        for user, user_attrs in filtered_users:
            org_id = user_attrs.get('custom:organizationId')
            org_name = None
            if org_id:
                try:
                    org = get_organization(org_id)
                    if org:
                        org_name = org.get('name')
                except:
                    pass

            result.append({
                'username': user['Username'],
                'status': user['UserStatus'],
                'organizationId': org_id,
                'organizationName': org_name,
                'email': user_attrs.get('email', ''),
                'parentOrganizationId': user_attrs.get('custom:parentOrganizationId'),
                'created': user['UserCreateDate'].isoformat()
            })
        return result
    except ClientError as e:
        raise ApplicationException(500, str(e))

def admin_get_user(user_pool_id, email, cognito_client=None):
    if cognito_client is None:
        cognito_client = boto3.client('cognito-idp')
        
    try:
        # メールアドレスを使用してユーザーを検索
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
        if e.response['Error']['Code'] == 'UserNotFoundException':
            return None
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
    cognito_client = _get_cognito_client(cognito_client)
    
    try:
        users = _get_all_users(user_pool_id, cognito_client, ['email', 'custom:organizationId'])
        filtered_users = _filter_users_by_organization(users, organization_id)
        return list({user_attrs.get('email') for _, user_attrs in filtered_users if user_attrs.get('email')})
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
    cognito_client = _get_cognito_client(cognito_client)
    
    try:
        users = _get_all_users(user_pool_id, cognito_client)
        filtered_users = _filter_users_by_organization(users, organization_id)
        return list({user_attrs.get('sub') for _, user_attrs in filtered_users if user_attrs.get('sub')})
    except Exception as e:
        raise ApplicationException(500, f"Error getting admin subs: {str(e)}")