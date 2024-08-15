import json
import logging
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ses = boto3.client('ses')

def lambda_handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")
    try:
        if 'httpMethod' in event:
            http_method = event['httpMethod']
        elif 'operation' in event:
            http_method = event['operation']
        else:
            logger.error("Invalid event structure")
            return create_response(400, 'Invalid event structure')

        if http_method == 'checkEmailVerification':
            return handle_check_email_verification(event)
        elif http_method == 'verifyEmailAddress':
            return handle_verify_email_address(event)

    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return create_response(500, f'Internal server error: {str(e)}')

def handle_check_email_verification(event):
    params = event.get('queryStringParameters') or event.get('payload') or {}
    email = params.get('email')
    
    if not email:
        return create_response(400, 'Missing email parameter')
    
    try:
        response = ses.get_identity_verification_attributes(
            Identities=[email]
        )
        verification_attrs = response['VerificationAttributes'].get(email, {})
        verification_status = verification_attrs.get('VerificationStatus', 'NotVerified')
        
        if verification_status == 'Success':
            return create_response(200, {'email': email, 'status': 'Success'})
        elif verification_status == 'Pending':
            return create_response(200, {'email': email, 'status': 'Pending'})
        else:
            return create_response(200, {'email': email, 'status': 'Failed'})
    
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'MessageRejected':
            return create_response(400, {'email': email, 'status': 'Failed', 'message': 'Email address is not verified'})
        else:
            logger.error(f"Error checking email verification: {str(e)}", exc_info=True)
            return create_response(500, {'email': email, 'status': 'Error', 'message': str(e)})

def handle_verify_email_address(event):
    params = event.get('queryStringParameters') or event.get('payload') or {}
    email = params.get('email')
    
    if not email:
        return create_response(400, 'Missing email parameter')
    
    try:
        response = ses.verify_email_identity(
            EmailAddress=email
        )
        return create_response(200, {'email': email, 'status': True})
    except Exception as e:
        logger.error(f"Error checking email verification: {str(e)}", exc_info=True)
        return create_response(500, f'Error checking email verification: {str(e)}')

def create_response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
        },
        'body': body
    }