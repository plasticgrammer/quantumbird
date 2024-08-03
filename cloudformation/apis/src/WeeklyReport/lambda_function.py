import json
import logging
import boto3
from boto3.dynamodb.conditions import Key
import os
from decimal import Decimal
from datetime import datetime, timedelta

print('Loading function')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
stage = os.environ.get('STAGE', 'dev')
weekly_reports_table_name = f'{stage}-WeeklyReports'
members_table_name = f'{stage}-Members'
weekly_reports_table = dynamodb.Table(weekly_reports_table_name)
members_table = dynamodb.Table(members_table_name)

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
        elif http_method == 'getReportStatus':
            return handle_get_report_status(event)
        elif http_method == 'getOvertimeData':
            return handle_get_overtime_data(event)
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
        return create_response(200, item)
    elif 'organizationId' in params and 'weekString' in params:
        items = get_reports_by_organization(params['organizationId'], params['weekString'])
        return create_response(200, items)
    else:
        return create_response(400, 'Invalid query parameters')

def handle_post(event):
    report_data = parse_body(event)
    item = prepare_item(report_data)
    response = weekly_reports_table.put_item(Item=item)
    logger.info(f"DynamoDB response: {response}")
    return create_response(201, 'Weekly report created successfully')

def handle_put(event):
    report_data = parse_body(event)
    member_uuid = report_data.get('memberUuid')
    week_string = report_data.get('weekString')
    
    if not member_uuid or not week_string:
        return create_response(400, 'Missing memberUuid or weekString')

    try:
        # 既存のレポートを取得
        existing_report = get_report(member_uuid, week_string)
        
        if not existing_report:
            return create_response(404, 'Report not found')

        # 新しいフィードバックを追加
        new_feedback = report_data.get('newFeedback')
        if new_feedback:
            feedbacks = existing_report.get('feedbacks', [])
            feedbacks.append({
                'content': new_feedback,
                'createdAt': datetime.now().isoformat()
            })
            report_data['feedbacks'] = feedbacks

        # その他のフィールドを更新
        updated_item = prepare_item(report_data, existing_report)
        
        response = weekly_reports_table.put_item(Item=updated_item)
        logger.info(f"DynamoDB response: {response}")
        return create_response(200, 'Weekly report updated successfully')
    except Exception as e:
        logger.error(f"Error updating report: {str(e)}", exc_info=True)
        return create_response(500, f'Failed to update report: {str(e)}')

def handle_delete(event):
    # API Gateway や直接呼び出しの両方に対応するようにパラメータ取得を修正
    params = event.get('queryStringParameters') or event.get('payload') or {}
    if 'memberUuid' not in params or 'weekString' not in params:
        return create_response(400, 'Missing required parameters')

    response = weekly_reports_table.delete_item(
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
        'improvements': report_data.get('improvements'),
        'status': report_data.get('status'),
        'feedbacks': report_data.get('feedbacks', []),
        'approvedAt': report_data.get('approvedAt'),
    }

def get_reports_by_organization(organization_id, week_string):
    try:
        response = weekly_reports_table.query(
            IndexName='OrganizationWeekIndex',
            KeyConditionExpression=Key('organizationId').eq(organization_id) & Key('weekString').eq(week_string)
        )
        return response['Items']
    except Exception as e:
        logger.error(f"Error querying reports: {str(e)}", exc_info=True)
        raise e

def get_report(member_uuid, week_string):
    try:
        response = weekly_reports_table.get_item(
            Key={
                'memberUuid': member_uuid,
                'weekString': week_string
            }
        )
        return response.get('Item')
    except Exception as e:
        logger.error(f"Error getting report: {str(e)}", exc_info=True)
        raise e

def handle_get_report_status(event):
    params = event.get('queryStringParameters') or event.get('payload') or {}
    if 'organizationId' not in params or 'weekString' not in params:
        return create_response(400, 'Missing required parameter')

    organization_id = params['organizationId']
    week_string = params['weekString']
    reports = get_reports_by_organization(organization_id, week_string)

    status = {
        'pending': 0,
        'inFeedback': 0,
        'confirmed': 0
    }

    for report in reports:
        report_status = report.get('status', 'pending')
        if report_status == 'approved':
            status['confirmed'] += 1
        elif report_status == 'feedback':
            status['inFeedback'] += 1
        else:
            status['pending'] += 1

    return create_response(200, status)

def get_member_names(member_uuids):
    member_names = {}
    for i in range(0, len(member_uuids), 100):
        batch = member_uuids[i:i+100]
        try:
            response = dynamodb.batch_get_item(
                RequestItems={
                    members_table_name: {
                        'Keys': [{'memberUuid': uuid} for uuid in batch],
                        'ProjectionExpression': 'memberUuid, #n',
                        'ExpressionAttributeNames': {'#n': 'name'}
                    }
                }
            )
            for item in response.get('Responses', {}).get(members_table_name, []):
                member_names[item['memberUuid']] = item.get('name', 'Unknown')
        except Exception as e:
            logger.error(f"Error fetching member names: {str(e)}", exc_info=True)
    
    return member_names

def handle_get_overtime_data(event):
    params = event.get('queryStringParameters') or event.get('payload') or {}
    if 'organizationId' not in params:
        return create_response(400, 'Missing organizationId parameter')

    organization_id = params['organizationId']
    weeks = get_last_5_weeks()
    overtime_data = {
        'labels': weeks,
        'datasets': []
    }

    members = {}
    member_uuids = set()
    for week in weeks:
        try:
            reports = get_reports_by_organization(organization_id, week)
            for report in reports:
                member_uuid = report['memberUuid']
                member_uuids.add(member_uuid)
                if member_uuid not in members:
                    members[member_uuid] = {
                        'data': [0] * 5
                    }
                week_index = weeks.index(week)
                members[member_uuid]['data'][week_index] = float(report.get('overtimeHours', 0))
        except Exception as e:
            logger.error(f"Error fetching reports for week {week}: {str(e)}", exc_info=True)
            # エラーが発生しても処理を続行し、取得できなかった週のデータは 0 として扱う

    # バッチでメンバー名を取得
    member_names = get_member_names(list(member_uuids))

    overtime_data['datasets'] = [
        {
            'label': member_names.get(member_uuid, f'Unknown ({member_uuid})'),
            'data': member_data['data']
        }
        for member_uuid, member_data in members.items()
    ]

    return create_response(200, overtime_data)

def get_previous_week_string():
    today = datetime.now()
    last_week = today - timedelta(weeks=1)
    return f"{last_week.year}-W{last_week.isocalendar()[1]:02d}"

def get_last_5_weeks():
    today = datetime.now()
    weeks = []
    for i in range(5):
        date = today - timedelta(weeks=i)
        weeks.append(f"{date.year}-W{date.isocalendar()[1]:02d}")
    return weeks[::-1]

def decimal_default_proc(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def create_response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            "content-type":"application/json",
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
        },
        'body': body
    }