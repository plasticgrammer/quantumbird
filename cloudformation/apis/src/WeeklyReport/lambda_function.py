import json
import logging
import boto3
from boto3.dynamodb.conditions import Key
import os
import time
import urllib.parse
from decimal import Decimal
from datetime import datetime, timedelta
from dateutil.parser import parse
from zoneinfo import ZoneInfo
import common.publisher
from common.utils import create_response

print('Loading function')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
stage = os.environ.get('STAGE', 'dev')
TIMEZONE = ZoneInfo(os.environ.get('TZ', 'UTC'))
BASE_URL = os.environ.get('BASE_URL', 'http://localhost:3000')

members_table_name = f'{stage}-Members'
organizations_table_name = f'{stage}-Organizations'
weekly_reports_table_name = f'{stage}-WeeklyReports'
organizations_table = dynamodb.Table(organizations_table_name)
members_table = dynamodb.Table(members_table_name)
weekly_reports_table = dynamodb.Table(weekly_reports_table_name)

def float_to_decimal(obj):
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: float_to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [float_to_decimal(v) for v in obj]
    return obj

def lambda_handler(event, context):
    #logger.info(f"Received event: {json.dumps(event)}")
    try:
        http_method = event['httpMethod']
        resource = event['resource']

        if http_method == 'GET':
            if resource == '/weekly-report':
                return handle_get(event)
            elif resource == '/weekly-report/status':
                return handle_get_report_status(event)
            elif resource == '/weekly-report/stats':
                return handle_get_stats_data(event)
        elif http_method == 'POST':
            if resource == '/weekly-report':
                return handle_post(event)
            elif resource == '/weekly-report/feedback':
                return handle_submit_feedback(event)
        elif http_method == 'PUT' and resource == '/weekly-report':
            return handle_put(event)
        elif http_method == 'DELETE' and resource == '/weekly-report':
            return handle_delete(event)
        else:
            return create_response(400, f'Unsupported method: {http_method}')
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return create_response(500, f'Internal server error: {str(e)}')

def handle_get(event):
    params = event.get('queryStringParameters', {}) or {}
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
    report_data = json.loads(event['body'], parse_float=Decimal)
    item = prepare_item(report_data)
    response = weekly_reports_table.put_item(Item=item)
    logger.info(f"DynamoDB response: {response}")
    return create_response(201, 'Weekly report created successfully')

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
        return None

def handle_put(event):
    report_data = json.loads(event['body'], parse_float=Decimal)
    member_uuid = report_data.get('memberUuid')
    week_string = report_data.get('weekString')

    if not member_uuid or not week_string:
        return create_response(400, 'Missing memberUuid or weekString')

    try:
        existing_report = get_report(member_uuid, week_string)
        if not existing_report:
            return create_response(404, 'Report not found')

        updated_item = prepare_item(report_data, existing_report)
        response = weekly_reports_table.put_item(Item=updated_item)
        logger.info(f"DynamoDB response: {response}")
        return create_response(200, 'Weekly report updated successfully')
    except Exception as e:
        logger.error(f"Error updating report: {str(e)}", exc_info=True)
        return create_response(500, f'Failed to update report: {str(e)}')

def handle_delete(event):
    params = event.get('queryStringParameters', {}) or {}
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


def prepare_item(report_data, existing_report=None):
    current_time = int(time.time())

    # Convert float values to Decimal
    converted_data = float_to_decimal(report_data)

    item = {
        'memberUuid': converted_data.get('memberUuid'),
        'weekString': converted_data.get('weekString'),
        'organizationId': converted_data.get('organizationId'),
        'projects': converted_data.get('projects'),
        'overtimeHours': converted_data.get('overtimeHours'),
        'issues': converted_data.get('issues'),
        'improvements': converted_data.get('improvements'),
        'rating': converted_data.get('rating', {}),
        'status': converted_data.get('status'),
        'feedbacks': converted_data.get('feedbacks', []),
        'approvedAt': converted_data.get('approvedAt'),
        'createdAt': current_time
    }
    
    if existing_report:
        # 既存のレポートの内容を保持しつつ、新しいデータで上書き
        existing_report.update(item)
        return existing_report
    
    return item

def get_reports_by_organization(organization_id, week_string):
    try:
        response = weekly_reports_table.query(
            IndexName='OrganizationWeekIndex',
            KeyConditionExpression=Key('organizationId').eq(organization_id) & Key('weekString').eq(week_string)
        )
        items = response['Items']
        return items
    except Exception as e:
        logger.error(f"Error querying reports for org {organization_id}, week {week_string}: {str(e)}", exc_info=True)
        return []  # Return an empty list instead of raising an exception

def handle_get_report_status(event):
    params = event.get('queryStringParameters', {}) or {}
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

def get_last_5_weeks():
    today = datetime.now(TIMEZONE)
    last_week = today - timedelta(days=today.weekday() + 7)  # 先週の月曜日
    weeks = []
    for i in range(5):
        week = last_week - timedelta(weeks=i)
        year = week.year
        week_number = week.isocalendar()[1]
        weeks.append(f"{year}-W{week_number:02d}")
    return list(reversed(weeks))

def handle_get_stats_data(event):
    params = event.get('queryStringParameters', {}) or {}
    if 'organizationId' not in params:
        return create_response(400, 'Missing organizationId parameter')

    organization_id = params['organizationId']
    weeks = get_last_5_weeks()
    
    stats_data = {
        'labels': ['5週前', '4週前', '3週前', '2週前', '先週'],
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
                        'data': [{
                            'week': w,
                            'overtimeHours': None,
                            'achievement': None,
                            'disability': None,
                            'stress': None
                        } for w in weeks]
                    }
                week_index = weeks.index(week)
                stats = members[member_uuid]['data'][week_index]
                
                # Safely convert overtimeHours to float
                overtime_hours = report.get('overtimeHours')
                stats['overtimeHours'] = float(overtime_hours) if overtime_hours is not None else 0

                rating = report.get('rating', {})
                stats['achievement'] = rating.get('achievement')
                stats['disability'] = rating.get('disability')
                stats['stress'] = rating.get('stress')
                
        except Exception as e:
            logger.error(f"Error processing reports for week {week}: {str(e)}", exc_info=True)
            # Continue to next week instead of breaking the loop

    member_names = get_member_names(list(member_uuids))
    logger.info(f"Retrieved names for {len(member_names)} members")

    stats_data['datasets'] = [
        {
            'label': member_names.get(member_uuid, f'Unknown ({member_uuid})'),
            'data': member_data['data']
        }
        for member_uuid, member_data in members.items()
    ]

    logger.info(f"Final stats_data: {json.dumps(stats_data, default=str)}")
    return create_response(200, stats_data)

def get_previous_week_string():
    today = datetime.now()
    last_week = today - timedelta(weeks=1)
    return f"{last_week.year}-W{last_week.isocalendar()[1]:02d}"

def handle_submit_feedback(event):
    params = json.loads(event['body'])
    member_uuid = params.get('memberUuid')
    week_string = params.get('weekString')
    feedback = params.get('feedback')

    if not all([member_uuid, week_string, feedback]):
        return create_response(400, 'Missing required parameters')

    try:
        existing_report = get_report(member_uuid, week_string)
        if not existing_report:
            return create_response(404, 'Report not found')

        feedbacks = existing_report.get('feedbacks', [])
        feedbacks.append(feedback)

        updated_item = {
            **existing_report,
            'feedbacks': feedbacks,
            'status': 'feedback'
        }

        response = weekly_reports_table.put_item(Item=updated_item)
        logger.info(f"DynamoDB response: {response}")

        member = get_member(member_uuid)
        if member:
            org_id = member.get('organizationId')
            if org_id:
                org = get_organization(org_id)
                if org:
                    send_feedback_mail(org, member, week_string, feedback)
                else:
                    logger.warning(f"Organization not found for ID: {org_id}")
            else:
                logger.warning(f"No organizationId found for member: {member_uuid}")
        else:
            logger.warning(f"Member not found: {member_uuid}")

        return create_response(200, 'Feedback submitted successfully')
    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}", exc_info=True)
        return create_response(500, f'Failed to submit feedback: {str(e)}')

def send_feedback_mail(organization, member, week_string, feedback):
    try:
        sendFrom = common.publisher.get_from_address(organization)
        subject = "【週次報告システム】管理者からのフィードバックがあります"
        bodyText = f"組織名：{organization['name']}\n\n"

        feedback_content = feedback.get('content')
        feedback_created_at = feedback.get('createdAt')

        # UTCからJSTに変換
        utc_dt = parse(feedback_created_at)
        jst_dt = utc_dt.astimezone(TIMEZONE)
        # 日本語の日付形式で文字列化
        formatted_date = jst_dt.strftime("%Y年%m月%d日 %H:%M")

        bodyText += f"管理者からのフィードバックがありました。（{formatted_date}）\n"
        bodyText += "------------------------------------------\n"
        bodyText += f"{feedback_content}\n"
        bodyText += "------------------------------------------\n"

        link = generate_report_link(organization['organizationId'], member["memberUuid"], week_string)
        link += '?feedback=true'
        bodyText += f"詳細はこちら: {link}"
        
        member_email = member.get('email')
        if member_email:
            common.publisher.send_mail(sendFrom, [member_email], subject, bodyText)
        else:
            logger.warning(f"No email address found for member: {member.get('memberUuid', 'Unknown UUID')}")
    except Exception as e:
        logger.error(f"Error sending feedback email: {str(e)}", exc_info=True)

def generate_report_link(organization_id, member_uuid, week_string):
    base_url = urllib.parse.urljoin(BASE_URL, "reports")
    
    # パスパラメータ
    path_params = [
        urllib.parse.quote(str(organization_id)),
        urllib.parse.quote(str(member_uuid)),
        urllib.parse.quote(week_string)
    ]    
    # URLの構築
    url = f"{base_url}/{'/'.join(path_params)}"    
    return url

def get_organization(organization_id):
    try:
        response = organizations_table.get_item(
            Key={
                'organizationId': organization_id
            }
        )
        return response.get('Item')
    except Exception as e:
        logger.error(f"Error getting organization: {str(e)}", exc_info=True)
        return None

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
        return None
