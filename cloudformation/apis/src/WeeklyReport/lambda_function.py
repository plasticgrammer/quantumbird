import json
import logging
import boto3
from boto3.dynamodb.conditions import Key
import os
from decimal import Decimal

print('Loading function')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
stage = os.environ.get('STAGE', 'dev')
table_name = f'{stage}-WeeklyReports'
table = dynamodb.Table(table_name)

def float_to_decimal(obj):
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: float_to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [float_to_decimal(v) for v in obj]
    return obj

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

        if http_method == 'GET' or http_method == 'get':
            return handle_get(event)
        elif http_method == 'POST' or http_method == 'create':
            return handle_post(event)
        elif http_method == 'PUT' or http_method == 'update':
            return handle_put(event)
        elif http_method == 'DELETE' or http_method == 'delete':
            return handle_delete(event)
        else:
            return create_response(400, f'Unsupported operation: {http_method}')
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return create_response(500, f'Internal server error: {str(e)}')

def handle_get(event):
    # API Gateway や直接呼び出しの両方に対応するようにパラメータ取得を修正
    params = event.get('queryStringParameters') or event.get('payload') or {}
    if not params:
        return create_response(400, 'Missing query parameters')

    if 'memberUuid' in params and 'weekString' in params:
        item = get_report(params['memberUuid'], params['weekString'])
        return create_response(200, json.dumps(item))
    elif 'organizationId' in params and 'weekString' in params:
        items = get_reports_by_organization(params['organizationId'], params['weekString'])
        return create_response(200, json.dumps(items))
    else:
        return create_response(400, 'Invalid query parameters')

def handle_post(event):
    report_data = parse_body(event)
    item = prepare_item(report_data)
    response = table.put_item(Item=item)
    logger.info(f"DynamoDB response: {response}")
    return create_response(201, 'Weekly report created successfully')

def handle_put(event):
    report_data = parse_body(event)
    item = prepare_item(report_data)
    response = table.put_item(Item=item)
    logger.info(f"DynamoDB response: {response}")
    return create_response(200, 'Weekly report updated successfully')

def handle_delete(event):
    # API Gateway や直接呼び出しの両方に対応するようにパラメータ取得を修正
    params = event.get('queryStringParameters') or event.get('payload') or {}
    if 'memberUuid' not in params or 'weekString' not in params:
        return create_response(400, 'Missing required parameters')

    response = table.delete_item(
        Key={
            'memberUuid': params['memberUuid'],
            'weekString': params['weekString']
        }
    )
    logger.info(f"DynamoDB response: {response}")
    return create_response(200, 'Weekly report deleted successfully')

def parse_body(event):
    if 'body' in event:
        return json.loads(event['body'], parse_float=Decimal)
    elif 'payload' in event:
        return float_to_decimal(event['payload'])
    else:
        return float_to_decimal(event)

def prepare_item(report_data):
    return {
        'memberUuid': report_data.get('memberUuid'),
        'weekString': report_data.get('weekString'),
        'organizationId': report_data.get('organizationId'),
        'projects': report_data.get('projects'),
        'overtimeHours': report_data.get('overtimeHours'),
        'issues': report_data.get('issues'),
        'achievements': report_data.get('achievements'),
        'improvements': report_data.get('improvements')
    }

def get_reports_by_organization(organization_id, week_string):
    try:
        response = table.query(
            IndexName='OrganizationWeekIndex',
            KeyConditionExpression=Key('organizationId').eq(organization_id) & Key('weekString').eq(week_string)
        )
        return response['Items']
    except Exception as e:
        logger.error(f"Error querying reports: {str(e)}", exc_info=True)
        raise e

def get_report(member_uuid, week_string):
    try:
        response = table.get_item(
            Key={
                'memberUuid': member_uuid,
                'weekString': week_string
            }
        )
        return response.get('Item')
    except Exception as e:
        logger.error(f"Error getting report: {str(e)}", exc_info=True)
        raise e

def decimal_default_proc(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def create_response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
        },
        'body': json.dumps(body, default=decimal_default_proc)
    }