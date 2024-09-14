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

def handle_check_email_verification(event):
    try:
        body = json.loads(event.get('body', '{}'))
        email = body.get('email')
    except json.JSONDecodeError:
        return create_response(400, 'Invalid JSON in request body')
    
    if not email:
        return create_response(400, 'Missing email parameter')
    
    try:
        response = ses.get_identity_verification_attributes(
            Identities=[email]
        )
        verification_attrs = response['VerificationAttributes'].get(email, {})
        verification_status = verification_attrs.get('VerificationStatus', 'NotVerified')
        
        return create_response(200, {
            'email': email,
            'status': verification_status
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
        ses.verify_email_identity(EmailAddress=email)
        return create_response(200, {
            'email': email,
            'status': 'Verification initiated'
        })
    except Exception as e:
        logger.error(f"Error initiating email verification: {str(e)}", exc_info=True)
        return create_response(500, {
            'email': email,
            'status': 'Error',
            'message': str(e)
        })
