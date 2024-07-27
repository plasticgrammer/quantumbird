import json
import logging
import boto3
from boto3.dynamodb.conditions import Key
import os
import uuid

print('Loading function')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
stage = os.environ.get('STAGE', 'dev')
members_table_name = f'{stage}-Members'
members_table = dynamodb.Table(members_table_name)

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

    if 'memberUuid' in params:
        if 'projects' in params:
            projects = get_member_projects(params['memberUuid'])
            return create_response(200, projects)
        else:
            member = get_member(params['memberUuid'])
            return create_response(200, member)
    elif 'organizationId' in params:
        members = list_members(params['organizationId'])
        return create_response(200, members)
    else:
        return create_response(400, 'Invalid query parameters')

def handle_post(event):
    data = parse_body(event)
    if 'memberUuid' in data:
        item = prepare_member_item(data)
        response = members_table.put_item(Item=item)
        logger.info(f"DynamoDB response: {response}")
        return create_response(201, 'Member created successfully')
    else:
        return create_response(400, 'Invalid data structure')

def handle_put(event):
    data = parse_body(event)
    if 'memberUuid' in data:
        if 'projects' in data:
            update_member_projects(data['memberUuid'], data['projects'])
            return create_response(200, 'Member projects updated successfully')
        else:
            item = prepare_member_item(data)
            response = members_table.put_item(Item=item)
            logger.info(f"Member update response: {response}")
            return create_response(200, 'Member updated successfully')
    else:
        return create_response(400, 'Invalid data structure')

def handle_delete(event):
    params = event.get('queryStringParameters') or event.get('payload') or {}
    if 'memberUuid' in params:
        delete_member(params['memberUuid'])
        return create_response(200, 'Member deleted successfully')
    else:
        return create_response(400, 'Missing required parameters')

def parse_body(event):
    if 'body' in event:
        return json.loads(event['body'])
    elif 'payload' in event:
        return event['payload']
    else:
        return event

def prepare_member_item(member_data):
    return {
        'memberUuid': member_data.get('memberUuid', str(uuid.uuid4())),
        'id': member_data.get('id'),
        'organizationId': member_data['organizationId'],
        'name': member_data.get('name'),
        'email': member_data.get('email'),
        'projects': member_data.get('projects', [])
    }

def get_member(member_uuid):
    try:
        response = members_table.get_item(
            Key={
                'memberUuid': member_uuid
            }
        )
        return response.get('Item')
    except Exception as e:
        logger.error(f"Error getting member: {str(e)}", exc_info=True)
        raise e

def get_member_projects(member_uuid):
    try:
        response = members_table.get_item(
            Key={
                'memberUuid': member_uuid
            },
            ProjectionExpression='projects'
        )
        return response.get('Item', {}).get('projects', [])
    except Exception as e:
        logger.error(f"Error getting member projects: {str(e)}", exc_info=True)
        raise e

def list_members(organization_id):
    try:
        response = members_table.query(
            IndexName='OrganizationIndex',
            KeyConditionExpression=Key('organizationId').eq(organization_id)
        )
        members = response['Items']
        # IDの昇順でソート
        sorted_members = sorted(members, key=lambda x: x.get('id', ''))
        return sorted_members
    except Exception as e:
        logger.error(f"Error listing members: {str(e)}", exc_info=True)
        raise e

def update_member_projects(member_uuid, projects):
    try:
        response = members_table.update_item(
            Key={'memberUuid': member_uuid},
            UpdateExpression="SET projects = :p",
            ExpressionAttributeValues={':p': projects},
            ReturnValues="UPDATED_NEW"
        )
        logger.info(f"Update member projects response: {response}")
        return response
    except Exception as e:
        logger.error(f"Error updating member projects: {str(e)}", exc_info=True)
        raise e

def delete_member(member_uuid):
    try:
        members_table.delete_item(
            Key={
                'memberUuid': member_uuid
            }
        )
    except Exception as e:
        logger.error(f"Error deleting member: {str(e)}", exc_info=True)
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