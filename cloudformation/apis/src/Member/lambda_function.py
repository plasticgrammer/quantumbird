

import json
import logging
import boto3
from boto3.dynamodb.conditions import Key
import os
import uuid
from decimal import Decimal

print('Loading function')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
stage = os.environ.get('STAGE', 'dev')
members_table_name = f'{stage}-Members'
members_table = dynamodb.Table(members_table_name)

def lambda_handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")
    try:
        http_method = event['httpMethod']
        resource = event['resource']

        if resource == '/member/project' and http_method == 'GET':
            return handle_get_projects(event)
        elif resource == '/member/mail' and http_method == 'PUT':
            return handle_put_email_confirmed(event)
        elif resource == '/member':
            if http_method == 'GET':
                return handle_get(event)
            elif http_method == 'POST':
                return handle_post(event)
            elif http_method == 'PUT':
                return handle_put(event)
            elif http_method == 'DELETE':
                return handle_delete(event)
        
        return create_response(400, {'message': f'Unsupported method: {http_method} or resource: {resource}'})
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return create_response(500, {'message': f'Internal server error: {str(e)}'})

def handle_get_projects(event):
    params = event.get('queryStringParameters', {}) or {}
    if 'memberUuid' not in params:
        return create_response(400, {'message': 'Missing memberUuid parameter'})
    
    projects = get_member_projects(params['memberUuid'])
    return create_response(200, projects)

def handle_get(event):
    params = event.get('queryStringParameters', {}) or {}
    if not params:
        return create_response(400, {'message': 'Missing query parameters'})

    if 'memberUuid' in params:
        member = get_member(params['memberUuid'])
        return create_response(200, member)
    elif 'organizationId' in params:
        members = list_members(params['organizationId'])
        return create_response(200, members)
    else:
        return create_response(400, {'message': 'Invalid query parameters'})

def handle_post(event):
    data = json.loads(event['body'])
    if 'memberUuid' in data:
        item = prepare_member_item(data)
        response = members_table.put_item(Item=item)
        logger.info(f"DynamoDB response: {response}")
        return create_response(201, {'message': 'Member created successfully'})
    else:
        return create_response(400, {'message': 'Invalid data structure'})

def handle_put(event):
    data = json.loads(event['body'])
    if 'memberUuid' in data:
        member_uuid = data['memberUuid']
        member = get_member(member_uuid)
        
        if member is None:
            return create_response(404, {'message': f'Member with UUID {member_uuid} not found'})

        if 'projects' in data:
            update_member_projects(member_uuid, data['projects'])
            return create_response(200, {'message': 'Member projects updated successfully'})
        else:
            item = prepare_member_item(data)
            response = members_table.put_item(Item=item)
            logger.info(f"Member update response: {response}")
            return create_response(200, {'message': 'Member updated successfully'})
    else:
        return create_response(400, {'message': 'Invalid data structure'})

def handle_put_email_confirmed(event):
    data = json.loads(event['body'])
    if 'memberUuid' in data:
        member_uuid = data['memberUuid']
        member = get_member(member_uuid)        
        if member is None:
            return create_response(404, {'message': f'Member with UUID {member_uuid} not found'})

        member['emailConfirmed'] = True
        response = members_table.put_item(Item=member)
        return create_response(200, {
            'message': 'Member email verified successfully',
            'email': member['email']
        })
    else:
        return create_response(400, {'message': 'Invalid data structure'})

def handle_delete(event):
    params = event.get('queryStringParameters', {}) or {}
    if 'memberUuid' in params:
        delete_member(params['memberUuid'])
        return create_response(200, {'message': 'Member deleted successfully'})
    else:
        return create_response(400, {'message': 'Missing required parameters'})

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
        item = response.get('Item')
        if item is None:
            logger.warning(f"Member with UUID {member_uuid} not found")
        return item
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
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
        },
        'body': json.dumps(body, default=decimal_default_proc)
    }

def decimal_default_proc(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError