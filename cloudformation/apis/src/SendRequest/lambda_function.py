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
from common.utils import create_response

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
    #logger.info(f"Received event: {json.dumps(event)}")
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

    for member in members_without_report:
        sendTo = [member.get("email")]
        bodyText = f"組織名：{organization['name']}\n"
        bodyText += f"{member.get("name", "-")}さん\n\n"
        bodyText += "システムからの報告依頼です。\n下記リンクより週次報告をお願いします。\n"
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
    """
    指定された日付と週オフセットから ISO 8601 形式の週文字列を生成する
    
    Args:
        current_date: 基準日（datetime, date, または 'YYYY-MM-DD' 形式の文字列）
        week_offset: 週オフセット（整数。負数の場合は過去の週を指定）
    
    Returns:
        str: ISO 8601形式の週文字列（例: '2024-W43'）
    """
    # 引数の型チェックと変換
    if isinstance(week_offset, decimal.Decimal):
        week_offset = int(week_offset)
    elif not isinstance(week_offset, int):
        try:
            week_offset = int(week_offset)
        except ValueError:
            logger.error(f"Invalid week_offset value: {week_offset}")
            week_offset = 0

    # 日付オブジェクトに変換
    if isinstance(current_date, str):
        current_date = datetime.strptime(current_date, "%Y-%m-%d").replace(tzinfo=TIMEZONE).date()
    elif isinstance(current_date, datetime):
        current_date = current_date.date()
    
    # その週の月曜日を取得
    monday = current_date - timedelta(days=current_date.weekday())
    
    # オフセットを適用（週の開始日である月曜日に対して適用）
    target_monday = monday + timedelta(weeks=week_offset)
    
    # 木曜日を取得（ISO 8601では木曜日が週の代表日）
    target_thursday = target_monday + timedelta(days=3)
    
    # その年の最初の木曜日を計算
    first_day = datetime(target_thursday.year, 1, 1, tzinfo=TIMEZONE).date()
    first_thursday = first_day + timedelta(days=(3 - first_day.weekday() + 7) % 7)
    
    # 週番号を計算
    calendar_week = ((target_thursday - first_thursday).days // 7) + 1
    
    # 年をまたぐ特殊なケースの処理
    if calendar_week < 1:
        # 前年の最後の週に属する場合
        target_thursday = target_thursday - timedelta(days=7)
        return get_string_from_week(target_thursday, 0)
    elif calendar_week > 52 and target_thursday.month == 12:
        # 次年の最初の週に属する可能性がある場合
        next_first_day = datetime(target_thursday.year + 1, 1, 1, tzinfo=TIMEZONE).date()
        next_first_thursday = next_first_day + timedelta(days=(3 - next_first_day.weekday() + 7) % 7)
        if target_thursday >= next_first_thursday - timedelta(days=3):
            # 次年の最初の週に属する
            return f"{target_thursday.year + 1}-W01"
    
    # 結果の文字列を生成
    return f"{target_thursday.year}-W{calendar_week:02d}"
