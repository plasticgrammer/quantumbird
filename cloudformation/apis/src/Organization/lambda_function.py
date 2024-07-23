import json
import logging
import boto3
from boto3.dynamodb.conditions import Key
import os

print('Loading function')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
stage = os.environ.get('STAGE', 'dev')
table_name = f'{stage}-Organizations'
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")
    try:
        # Check if the event is from API Gateway or direct invocation
        if 'httpMethod' in event:
            # API Gateway request
            http_method = event['httpMethod']
        elif 'operation' in event:
            # Direct invocation
            http_method = event['operation']
        else:
            logger.error("Invalid event structure")
            return create_response(400, 'Invalid event structure')

        if http_method in ['GET', 'get']:
            return handle_get(event)
        elif http_method in ['POST', 'create']:
            return handle_post(event)
        elif http_method in ['PUT', 'update']:
            return handle_put(event)
        elif http_method in ['DELETE', 'delete']:
            return handle_delete(event)
        else:
            return create_response(400, f'Unsupported operation: {http_method}')
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return create_response(500, f'Internal server error: {str(e)}')

def handle_get(event):
    params = event.get('queryStringParameters') or event.get('payload') or {}
    if not params:
        return create_response(400, 'Missing query parameters')

    if 'organizationId' in params:
        item = get_organization(params['organizationId'])
        return create_response(200, json.dumps(item))
    else:
        items = list_organizations()
        return create_response(200, json.dumps(items))

def handle_post(event):
    org_data = parse_body(event)
    item = prepare_item(org_data)
    response = table.put_item(Item=item)
    logger.info(f"DynamoDB response: {response}")
    return create_response(201, 'Organization created successfully')

def handle_put(event):
    org_data = parse_body(event)
    item = prepare_item(org_data)
    response = table.put_item(Item=item)
    logger.info(f"DynamoDB response: {response}")
    return create_response(200, 'Organization updated successfully')

def handle_delete(event):
    params = event.get('queryStringParameters') or event.get('payload') or {}
    if 'organizationId' not in params:
        return create_response(400, 'Missing required parameters')

    response = table.delete_item(
        Key={
            'organizationId': params['organizationId']
        }
    )
    logger.info(f"DynamoDB response: {response}")
    return create_response(200, 'Organization deleted successfully')

def parse_body(event):
    if 'body' in event:
        return json.loads(event['body'])
    elif 'payload' in event:
        return event['payload']
    else:
        return event

def prepare_item(org_data):
    return {
        'organizationId': org_data.get('organizationId'),
        'name': org_data.get('name'),
        'members': org_data.get('members', [])
    }

def get_organization(organization_id):
    try:
        response = table.get_item(
            Key={
                'organizationId': organization_id
            }
        )
        return response.get('Item')
    except Exception as e:
        logger.error(f"Error getting organization: {str(e)}", exc_info=True)
        raise e

def list_organizations():
    try:
        response = table.scan()
        return response['Items']
    except Exception as e:
        logger.error(f"Error listing organizations: {str(e)}", exc_info=True)
        raise e

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