import json
import logging
import boto3
from boto3.dynamodb.conditions import Key
import os
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo
from common.utils import create_response
import common.dynamo_items as dynamo_items

print('Loading function')

TIMEZONE = ZoneInfo(os.environ.get('TZ', 'UTC'))

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
stage = os.environ.get('STAGE', 'dev')
tasks_table_name = f'{stage}-UserTasks'
tasks_table = dynamodb.Table(tasks_table_name)

def lambda_handler(event, context):
    #logger.info(f"Received event: {json.dumps(event)}")
    try:
        http_method = event['httpMethod']
        resource = event['resource']

        if http_method == 'GET':
            return handle_get(event)
        elif http_method == 'POST':
            return handle_post(event)
        elif http_method == 'PUT':
            return handle_put(event)
        elif http_method == 'DELETE':
            return handle_delete(event)
        else:
            return create_response(400, {'message': f'Unsupported method: {http_method}'})
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return create_response(500, {'message': f'Internal server error: {str(e)}'})

def handle_get(event):
    user_id = event['requestContext']['authorizer']['claims']['sub']
    params = event.get('queryStringParameters', {}) or {}
    if 'taskId' in params:
        task = get_task(user_id, params['taskId'])
        if task is None:
            return create_response(404, {'message': f"Task with id {params['taskId']} not found"})
        return create_response(200, task)
    else:
        tasks = list_tasks(user_id)
        return create_response(200, tasks)

def handle_post(event):
    user_id = event['requestContext']['authorizer']['claims']['sub']
    data = json.loads(event['body'])
    item = dynamo_items.prepare_task_item(user_id, data, TIMEZONE)
    response = tasks_table.put_item(Item=item)
    return create_response(201, item)

def handle_put(event):
    user_id = event['requestContext']['authorizer']['claims']['sub']
    data = json.loads(event['body'])
    if 'taskId' not in data:
        return create_response(400, {'message': 'taskId is required'})
    existing_task = get_task(user_id, data['taskId'])
    if existing_task is None:
        return create_response(404, {'message': f"Task with id {data['taskId']} not found"})
    item = dynamo_items.prepare_task_item(user_id, data, existing_task)
    response = tasks_table.put_item(Item=item)
    return create_response(200, item)

def handle_delete(event):
    user_id = event['requestContext']['authorizer']['claims']['sub']
    params = event.get('queryStringParameters', {}) or {}
    if 'taskId' not in params:
        return create_response(400, {'message': 'taskId is required'})
    delete_task(user_id, params['taskId'])
    return create_response(200, {'message': 'Task deleted successfully'})

def get_task(user_id, task_id):
    try:
        response = tasks_table.get_item(
            Key={
                'userId': user_id,
                'taskId': task_id
            }
        )
        return response.get('Item')
    except Exception as e:
        logger.error(f"Error getting task: {str(e)}", exc_info=True)
        return None

def list_tasks(user_id):
    try:
        response = tasks_table.query(
            KeyConditionExpression=Key('userId').eq(user_id)
        )
        tasks = response['Items']
        sorted_tasks = sorted(tasks, key=lambda x: x.get('createdAt', ''))
        return sorted_tasks
    except Exception as e:
        logger.error(f"Error listing tasks: {str(e)}", exc_info=True)
        raise e

def delete_task(user_id, task_id):
    try:
        tasks_table.delete_item(
            Key={
                'userId': user_id,
                'taskId': task_id
            }
        )
    except Exception as e:
        logger.error(f"Error deleting task: {str(e)}", exc_info=True)
        raise e
