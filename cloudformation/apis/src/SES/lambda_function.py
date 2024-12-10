import json
import logging
import common.publisher
from common.utils import create_response

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
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
        result = common.publisher.check_identity_verification(email)
        return create_response(200, result)
    except Exception as e:
        logger.error(f"Error checking email verification: {str(e)}", exc_info=True)
        return create_response(500, {'status': 'Error', 'message': str(e)})

def handle_verify_email_address(event):
    try:
        body = json.loads(event.get('body', '{}'))
        email = body.get('email')
    except json.JSONDecodeError:
        return create_response(400, 'Invalid JSON in request body')
    
    if not email:
        return create_response(400, 'Missing email parameter')
    
    try:
        # 現在の検証状態を確認
        status = common.publisher.check_identity_verification(email)
        if status['status'] == 'Success':
            return create_response(200, status)
        
        # 検証を開始
        common.publisher.verify_email_identity(email)
        return create_response(200, {
            'email': email,
            'status': 'Pending',
            'verifiedBy': 'email'
        })
    
    except Exception as e:
        logger.error(f"Error initiating email verification: {str(e)}", exc_info=True)
        return create_response(500, {'status': 'Error', 'message': str(e)})
