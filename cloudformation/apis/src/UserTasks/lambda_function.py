import json
import logging
import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal
import os
import uuid
import datetime

print('Loading function')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
stage = os.environ.get('STAGE', 'dev')
tasks_table_name = f'{stage}-UserTasks'
tasks_table = dynamodb.Table(tasks_table_name)

def lambda_handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")
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
    item = prepare_task_item(user_id, data)
    response = tasks_table.put_item(Item=item)
    return create_response(201, {'message': 'Task created successfully', 'task': item})

def handle_put(event):
    user_id = event['requestContext']['authorizer']['claims']['sub']
    data = json.loads(event['body'])
    if 'taskId' not in data:
        return create_response(400, {'message': 'taskId is required'})
    existing_task = get_task(user_id, data['taskId'])
    if existing_task is None:
        return create_response(404, {'message': f"Task with id {data['taskId']} not found"})
    item = prepare_task_item(user_id, data, existing_task)
    response = tasks_table.put_item(Item=item)
    return create_response(200, {'message': 'Task updated successfully', 'task': item})

def handle_delete(event):
    user_id = event['requestContext']['authorizer']['claims']['sub']
    params = event.get('queryStringParameters', {}) or {}
    if 'taskId' not in params:
        return create_response(400, {'message': 'taskId is required'})
    delete_task(user_id, params['taskId'])
    return create_response(200, {'message': 'Task deleted successfully'})

def prepare_task_item(user_id, task_data, existing_task=None):
    if existing_task is None:
        existing_task = {}

    current_time = datetime.datetime.now().isoformat()
    
    updated_task = {
        'UserId': user_id,
        'TaskId': task_data.get('taskId', existing_task.get('TaskId', str(uuid.uuid4()))),
        'Title': task_data.get('title', existing_task.get('Title')),
        'Done': task_data.get('status', existing_task.get('Done', False)),
        'CreatedAt': existing_task.get('CreatedAt', current_time),
        'UpdatedAt': current_time
    }
    return {k: v for k, v in updated_task.items() if v is not None}

def get_task(user_id, task_id):
    try:
        response = tasks_table.get_item(
            Key={
                'UserId': user_id,
                'TaskId': task_id
            }
        )
        return response.get('Item')
    except Exception as e:
        logger.error(f"Error getting task: {str(e)}", exc_info=True)
        return None

def list_tasks(user_id):
    try:
        response = tasks_table.query(
            KeyConditionExpression=Key('UserId').eq(user_id)
        )
        tasks = response['Items']
        sorted_tasks = sorted(tasks, key=lambda x: x.get('CreatedAt', ''))
        return sorted_tasks
    except Exception as e:
        logger.error(f"Error listing tasks: {str(e)}", exc_info=True)
        raise e

def delete_task(user_id, task_id):
    try:
        tasks_table.delete_item(
            Key={
                'UserId': user_id,
                'TaskId': task_id
            }
        )
    except Exception as e:
        logger.error(f"Error deleting task: {str(e)}", exc_info=True)
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