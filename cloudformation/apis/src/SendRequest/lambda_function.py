# スケジューラー関数
import boto3
import logging
import json
import os
import urllib.parse
import decimal
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from boto3.dynamodb.conditions import Key, Attr
import common.publisher

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 環境変数TZからタイムゾーンを取得
TIMEZONE = ZoneInfo(os.environ.get('TZ', 'UTC'))
BASE_URL = os.environ.get('BASE_URL', 'http://localhost:3000')
stage = os.environ.get('STAGE', 'dev')

dynamodb = boto3.resource('dynamodb')
organizations_table = dynamodb.Table(f'{stage}-Organizations')
members_table = dynamodb.Table(f'{stage}-Members')
weekly_reports_table = dynamodb.Table(f'{stage}-WeeklyReports')

def lambda_handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")
    try:
        # organization_idを編集
        organization_id = None
        if 'httpMethod' in event:
            payload = json.loads(event['body'])
            organization_id = payload.get('organizationId')
        else:
            organization_id = extract_organization_id(event)

        if not organization_id:
            raise ValueError("organization_id not found in the event")

        logger.info(f"Processing task for organization ID: {organization_id}")

        org = get_organization(organization_id)
        if not org:
            raise ValueError(f"Organization not found for ID: {organization_id}")

        # week_stringを編集
        if 'httpMethod' in event:
            week_string = payload.get('weekString')
        else:
            reportWeek = org.get('reportWeek', 0)
            if isinstance(reportWeek, decimal.Decimal):
                reportWeek = int(reportWeek)
            now = datetime.now(TIMEZONE)
            week_string = get_string_from_week(now, reportWeek)

        send_request_mail(org, week_string)

        return create_response(200, 'Processing completed successfully')

    except Exception as e:
        logger.error(f"Error processing event: {str(e)}", exc_info=True)
        return create_response(500, f'Error processing event: {str(e)}')

def extract_organization_id(event):
    if isinstance(event, str):
        event = json.loads(event)
    
    if not isinstance(event, dict):
        return None

    payload = event.get('payload', event)
    
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except json.JSONDecodeError:
            return None

    return payload.get('organizationId') or event.get('organizationId')

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

def send_request_mail(organization, week_string):
    organization_id = organization['organizationId']
    response = members_table.query(
        IndexName='OrganizationIndex',
        KeyConditionExpression=Key('organizationId').eq(organization_id)
    )
    members = response['Items']

    # 対象週に報告がないメンバーを特定
    members_without_report = get_members_without_report(organization_id, week_string, members)

    if not members_without_report:
        logger.info(f"No members without report for week {week_string}")
        return

    sendFrom = common.publisher.get_from_address(organization)
    subject = "【週次報告システム】週次報告をお願いします"
    bodyText = f"組織名：{organization['name']}\n\n"
    bodyText += "お疲れさまです。\n下記リンクより週次報告をお願いします。\n"

    for member in members_without_report:
        sendTo = [member.get("email")]
        link = generate_report_link(organization_id, member["memberUuid"], week_string)

        logger.info(f"Send mail from: {sendFrom}, to: {sendTo}")
        
        common.publisher.send_mail(sendFrom, sendTo, subject, bodyText + link)

def get_members_without_report(organization_id, week_string, members):
    # 指定された組織と週のすべてのレポートを取得
    reports = get_reports_by_organization(organization_id, week_string)
    
    # レポートを提出したメンバーのUUIDセットを作成
    reported_member_uuids = set(report['memberUuid'] for report in reports)
    
    # レポートを提出していないメンバーをフィルタリング
    members_without_report = [
        member for member in members 
        if member['memberUuid'] not in reported_member_uuids
    ]
    
    return members_without_report

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

def get_string_from_week(current_date, week_offset=0):
    # 引数の型チェックと変換
    if isinstance(week_offset, decimal.Decimal):
        week_offset = int(week_offset)
    elif not isinstance(week_offset, int):
        try:
            week_offset = int(week_offset)
        except ValueError:
            logger.error(f"Invalid week_offset value: {week_offset}")
            week_offset = 0  # デフォルト値を設定

    # 日付オブジェクトに変換（文字列が渡された場合に対応）
    if isinstance(current_date, str):
        current_date = datetime.strptime(current_date, "%Y-%m-%d").replace(tzinfo=TIMEZONE).date()
    elif isinstance(current_date, datetime):
        current_date = current_date.date()
    
    # オフセットを適用
    current_date += timedelta(weeks=week_offset)
    
    # 木曜日に移動（ISO 8601準拠）
    thursday = current_date + timedelta(days=(3 - current_date.weekday() + 7) % 7)
    
    # その年の最初の木曜日を計算
    first_thursday = datetime(thursday.year, 1, 1, tzinfo=TIMEZONE).date()
    if first_thursday.weekday() != 3:
        first_thursday = first_thursday + timedelta(days=(3 - first_thursday.weekday() + 7) % 7)
    
    # 週番号を計算
    week_number = (thursday - first_thursday).days // 7 + 1
    
    # 結果の文字列を生成
    return f"{thursday.year}-W{week_number:02d}"

def create_response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            "Content-Type": "application/json",
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
        },
        'body': json.dumps(body) if body else ''
    }