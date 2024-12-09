import json
import logging
import boto3
from botocore.exceptions import ClientError
from common.utils import create_response

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ses = boto3.client('ses')

def lambda_handler(event, context):
    #logger.info(f"Received event: {json.dumps(event)}")
    try:
        http_method = event['httpMethod']
        resource = event['resource']

        if http_method == 'OPTIONS':
            return create_response(200, {})
        elif http_method == 'POST' and resource == '/ses/check':
            return handle_check_email_verification(event)
        elif http_method == 'POST' and resource == '/ses/verify':
            return handle_verify_email_address(event)
        else:
            logger.error("Invalid HTTP method")
            return create_response(400, 'Invalid HTTP method')

    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return create_response(500, f'Internal server error: {str(e)}')

def check_domain_verification(domain):
    """ドメインの検証状態を確認"""
    try:
        response = ses.get_identity_verification_attributes(
            Identities=[domain]
        )
        verification_attrs = response['VerificationAttributes'].get(domain, {})
        return verification_attrs.get('VerificationStatus') == 'Success'
    except ClientError:
        return False

def handle_check_email_verification(event):
    try:
        body = json.loads(event.get('body', '{}'))
        email = body.get('email')
    except json.JSONDecodeError:
        return create_response(400, 'Invalid JSON in request body')
    
    if not email:
        return create_response(400, 'Missing email parameter')
    
    try:
        # ドメインの検証状態を確認
        domain = email.split('@')[1]
        is_domain_verified = check_domain_verification(domain)
        
        if is_domain_verified:
            # ドメインが検証済みの場合は、メールアドレスも検証済みとして扱う
            return create_response(200, {
                'email': email,
                'status': 'Success',
                'verifiedBy': 'domain'
            })
        
        # ドメインが未検証の場合は、メールアドレス個別の検証状態を確認
        response = ses.get_identity_verification_attributes(
            Identities=[email]
        )
        verification_attrs = response['VerificationAttributes'].get(email, {})
        verification_status = verification_attrs.get('VerificationStatus', 'NotVerified')
        
        return create_response(200, {
            'email': email,
            'status': verification_status,
            'verifiedBy': 'email'
        })
    
    except ClientError as e:
        logger.error(f"Error checking email verification: {str(e)}", exc_info=True)
        return create_response(500, {
            'email': email,
            'status': 'Error',
            'message': str(e)
        })

def handle_verify_email_address(event):
    try:
        body = json.loads(event.get('body', '{}'))
        email = body.get('email')
    except json.JSONDecodeError:
        return create_response(400, 'Invalid JSON in request body')
    
    if not email:
        return create_response(400, 'Missing email parameter')
    
    try:
        # ドメインの検証状態を確認
        domain = email.split('@')[1]
        is_domain_verified = check_domain_verification(domain)
        
        if is_domain_verified:
            # ドメインが検証済みの場合は、追加の検証は不要
            return create_response(200, {
                'email': email,
                'status': 'Success',
                'verifiedBy': 'domain'
            })
        
        # ドメインが未検証の場合は、メールアドレスの検証を開始
        ses.verify_email_identity(EmailAddress=email)
        return create_response(200, {
            'email': email,
            'status': 'Verification initiated',
            'verifiedBy': 'email'
        })
    except Exception as e:
        logger.error(f"Error initiating email verification: {str(e)}", exc_info=True)
        return create_response(500, {
            'email': email,
            'status': 'Error',
            'message': str(e)
        })
