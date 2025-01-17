import json
import logging
import boto3
from boto3.dynamodb.conditions import Key
import os
import time
import urllib.parse
from decimal import Decimal, InvalidOperation
from datetime import datetime, timedelta
from dateutil.parser import parse
from zoneinfo import ZoneInfo
import common.publisher
from common.utils import create_response
import common.dynamo_items as dynamo_items

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

def lambda_handler(event, context):
    #logger.info(f"Received event: {json.dumps(event)}")
    try:
        http_method = event['httpMethod']
        resource = event['resource']

        if http_method == 'GET':
            if resource == '/weekly-report':
                return handle_get(event)
            elif resource == '/weekly-report/member/{memberUuid}':
                return handle_get_member_reports(event)
            elif resource == '/weekly-report/status':
                return handle_get_report_status(event)
            elif resource == '/weekly-report/stats':
                return handle_get_stats_data(event)
            elif resource == '/weekly-report/export':
                return handle_export(event)
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
    item = dynamo_items.prepare_weekly_report_item(report_data, TIMEZONE)
    response = weekly_reports_table.put_item(Item=item)
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

        updated_item = dynamo_items.prepare_weekly_report_item(report_data, existing_report, TIMEZONE)
        response = weekly_reports_table.put_item(Item=updated_item)
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
    return create_response(200, 'Weekly report deleted successfully')

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
        'pending': {'count': 0, 'members': []},
        'inFeedback': {'count': 0, 'members': []},
        'confirmed': {'count': 0, 'members': []},
        'none': {'count': 0, 'members': []}
    }

    reported_member_uuids = set()
    for report in reports:
        report_status = report.get('status', 'pending')
        member_uuid = report.get('memberUuid')
        reported_member_uuids.add(member_uuid)
        if report_status == 'approved':
            status['confirmed']['count'] += 1
            status['confirmed']['members'].append(member_uuid)
        elif report_status == 'feedback':
            status['inFeedback']['count'] += 1
            status['inFeedback']['members'].append(member_uuid)
        else:
            status['pending']['count'] += 1
            status['pending']['members'].append(member_uuid)

    # Get all members of the organization
    all_members = get_all_members(organization_id)
    all_member_uuids = [member['memberUuid'] for member in all_members]

    # Identify members with no reports
    no_report_members = set(all_member_uuids) - reported_member_uuids
    status['none']['count'] = len(no_report_members)
    status['none']['members'] = list(no_report_members)

    # Get member names
    member_names = get_member_names(all_member_uuids)

    # Convert member UUIDs to names
    for key in status:
        status[key]['members'] = [member_names.get(uuid, 'Unknown') for uuid in status[key]['members']]

    return create_response(200, status)

def get_all_members(organization_id):
    try:
        response = members_table.query(
            IndexName='OrganizationIndex',
            KeyConditionExpression=Key('organizationId').eq(organization_id)
        )
        return response.get('Items', [])
    except Exception as e:
        logger.error(f"Error fetching all members for organization {organization_id}: {str(e)}", exc_info=True)
        return []

def get_member_names(member_uuids):
    member_info = {}
    for i in range(0, len(member_uuids), 100):
        batch = member_uuids[i:i+100]
        try:
            response = dynamodb.batch_get_item(
                RequestItems={
                    members_table_name: {
                        'Keys': [{'memberUuid': uuid} for uuid in batch],
                        'ProjectionExpression': 'memberUuid, #n, id',
                        'ExpressionAttributeNames': {'#n': 'name'}
                    }
                }
            )
            for item in response.get('Responses', {}).get(members_table_name, []):
                member_info[item['memberUuid']] = {
                    'name': item.get('name', 'Unknown'),
                    'id': item.get('id')
                }
        except Exception as e:
            logger.error(f"Error fetching member info: {str(e)}", exc_info=True)
    
    return member_info

def get_last_5_weeks():
    """5週前から先週までの週番号を取得（今週は含まない）
    Returns:
        list: ['YYYY-WNN'形式の週番号文字列のリスト（古い順）]
    """
    today = datetime.now(TIMEZONE)
    
    def get_iso_week(date):
        return date.isocalendar()[:2]  # (year, week)を返す
    
    # 先週の月曜日を取得
    last_monday = today - timedelta(days=today.weekday() + 7)
    weeks = []
    
    # 5週前から先週までの週番号を取得
    for i in range(4, -1, -1):  # 4,3,2,1,0 の順で処理（新しい順）
        target_date = last_monday - timedelta(weeks=i)
        year, week = get_iso_week(target_date)
        weeks.append(f"{year}-W{week:02d}")
    
    return weeks  # 古い順に自然と並ぶ

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

    member_info = get_member_names(list(member_uuids))

    # データセットの作成とソート
    stats_data['datasets'] = [
        {
            'memberUuid': member_uuid,
            'id': member_info.get(member_uuid, {}).get('id', 0),
            'label': member_info.get(member_uuid, {}).get('name', f'Unknown ({member_uuid})'),
            'data': member_data['data']
        }
        for member_uuid, member_data in members.items()
    ]
    
    # idでソート
    stats_data['datasets'].sort(key=lambda x: x.get('id', 0))

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
        bodyText = f"組織名：{organization['name']}\n"
        bodyText += f"{member.get('name', '-')}さん\n\n"

        feedback_content = feedback.get('content')
        feedback_created_at = feedback.get('createdAt')

        utc_dt = parse(feedback_created_at)
        jst_dt = utc_dt.astimezone(TIMEZONE)
        formatted_date = jst_dt.strftime("%Y年%m月%d日 %H:%M")

        bodyText += f"管理者からのフィードバックがありました。（{formatted_date}）\n"
        bodyText += "------------------------------------------\n"
        bodyText += f"{feedback_content}\n"
        bodyText += "------------------------------------------\n\n"

        link = generate_report_link(organization['organizationId'], member["memberUuid"], week_string)
        link += '?feedback=true'
        bodyText += f"下記リンクより内容確認および返信が可能です。\n{link}"
        
        member_email = member.get('email')
        if (member_email):
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

def handle_export(event):
    """組織単位での週次レポートデータのエクスポートを処理する"""
    params = event.get('queryStringParameters', {}) or {}
    if 'organizationId' not in params:
        return create_response(400, 'Missing organizationId parameter')

    organization_id = params['organizationId']
    
    try:
        # WeeklyReportsテーブルから対象組織の全データを取得
        reports = get_all_organization_reports(organization_id)
        
        # レポートからmemberUuidの一覧を抽出
        member_uuids = list(set(report['memberUuid'] for report in reports))
        
        # メンバー名の取得
        member_names = get_member_names(member_uuids)
        
        # レポートデータの整形
        formatted_reports = format_export_data(reports, member_names)
        
        return create_response(200, formatted_reports)
    except Exception as e:
        logger.error(f"Error exporting reports: {str(e)}", exc_info=True)
        return create_response(500, f'Failed to export reports: {str(e)}')

def get_all_organization_reports(organization_id):
    """組織の全週次レポートを取得する"""
    reports = []
    last_evaluated_key = None
    
    while True:
        query_params = {
            'IndexName': 'OrganizationWeekIndex',
            'KeyConditionExpression': Key('organizationId').eq(organization_id)
        }
        
        if last_evaluated_key:
            query_params['ExclusiveStartKey'] = last_evaluated_key
            
        response = weekly_reports_table.query(**query_params)
        reports.extend(response.get('Items', []))
        
        last_evaluated_key = response.get('LastEvaluatedKey')
        if not last_evaluated_key:
            break
    
    return reports

def format_export_data(reports, member_names):
    """エクスポート用にレポートデータを整形する"""
    formatted_reports = []
    
    for report in reports:
        try:
            # タイムスタンプの処理を安全に行う
            created_at = format_timestamp(report.get('createdAt', 0))
            approved_at = format_timestamp(report.get('approvedAt')) if report.get('approvedAt') else None
            
            # 数値データの安全な変換
            overtime_hours = safe_float_conversion(report.get('overtimeHours'))
            
            # 基本データの整形
            formatted_report = {
                'memberName': member_names.get(report['memberUuid'], f"Unknown ({report['memberUuid']})"),
                'weekString': report['weekString'],
                'status': report.get('status', 'pending'),
                'overtimeHours': overtime_hours,
                'projects': report.get('projects', []),
                'issues': report.get('issues', ''),
                'improvements': report.get('improvements', ''),
                'stressHelp': report.get('stressHelp', ''),
                'rating': {
                    'achievement': safe_float_conversion(report.get('rating', {}).get('achievement')),
                    'disability': safe_float_conversion(report.get('rating', {}).get('disability')),
                    'stress': safe_float_conversion(report.get('rating', {}).get('stress'))
                },
                'feedbacks': report.get('feedbacks', []),
                'createdAt': created_at,
                'approvedAt': approved_at
            }
            
            formatted_reports.append(formatted_report)
        except Exception as e:
            logger.error(f"Error formatting report for week {report.get('weekString')}: {str(e)}")
            continue
    
    # 週とメンバー名でソート
    formatted_reports.sort(key=lambda x: (x['weekString'], x['memberName']))
    
    return formatted_reports

def safe_float_conversion(value, default=0.0):
    """安全に浮動小数点数に変換する
    
    Parameters:
        value: 変換する値
        default: デフォルト値（変換できない場合に返す値）
    
    Returns:
        float: 変換された浮動小数点数またはデフォルト値
    """
    if value is None:
        return default
        
    try:
        if isinstance(value, (Decimal, float, int)):
            return float(value)
        elif isinstance(value, str):
            return float(value.strip())
        return default
    except (ValueError, TypeError, InvalidOperation):
        logger.warning(f"Failed to convert value to float: {value}")
        return default

def format_timestamp(timestamp):
    """タイムスタンプを日時文字列に変換する
    
    Parameters:
        timestamp: Unix timestamp (int or str) or ISO format string
    
    Returns:
        str: フォーマットされた日時文字列
    """
    try:
        if timestamp is None:
            return None
            
        # 整数（Unix タイムスタンプ）の場合
        if isinstance(timestamp, (int, float, Decimal)):
            return datetime.fromtimestamp(float(timestamp), TIMEZONE).strftime('%Y-%m-%d %H:%M:%S')
        
        # 文字列の場合
        if isinstance(timestamp, str):
            # Unix タイムスタンプとして解釈できる場合
            try:
                return datetime.fromtimestamp(float(timestamp), TIMEZONE).strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                # ISO形式の文字列として解釈
                try:
                    return parse(timestamp).astimezone(TIMEZONE).strftime('%Y-%m-%d %H:%M:%S')
                except ValueError:
                    logger.warning(f"Unable to parse timestamp: {timestamp}")
                    return timestamp
        
        return None
    except Exception as e:
        logger.error(f"Error formatting timestamp {timestamp}: {str(e)}")
        return None

def handle_get_member_reports(event):
    member_uuid = event['pathParameters']['memberUuid']
    try:
        weeks = get_last_5_weeks()
        reports = []
        
        for week in weeks:
            report = get_report(member_uuid, week)
            if report:
                reports.append(report)
            else:
                reports.append({
                    'memberUuid': member_uuid,
                    'weekString': week,
                    'status': 'none'
                })
        
        return create_response(200, reports)
    except Exception as e:
        logger.error(f"Error getting member reports: {str(e)}", exc_info=True)
        return create_response(500, f'Failed to get member reports: {str(e)}')