# スケジューラー関数
import boto3
import logging
import json
import os
import pytz
import urllib.parse
from datetime import datetime
from boto3.dynamodb.conditions import Key
import common.publisher

logger = logging.getLogger()
logger.setLevel(logging.INFO)

TIMEZONE = os.environ.get('TIMEZONE', 'UTC')
BASE_URL = os.environ.get('BASE_URL', 'http://localhost:3000')
stage = os.environ.get('STAGE', 'dev')

dynamodb = boto3.resource('dynamodb')
organizations_table_name = f'{stage}-Organizations'
members_table_name = f'{stage}-Members'
organizations_table = dynamodb.Table(organizations_table_name)
members_table = dynamodb.Table(members_table_name)

def scheduler_handler(event, context):
    
    # 現在の曜日と時間を取得
    tz = pytz.timezone(TIMEZONE)
    now = datetime.now(tz)
    current_day = now.weekday()
    current_time = f"{now.hour:02d}:00"
    
    # 現在の曜日と時間に一致する設定を検索
    response = organizations_table.scan(
        FilterExpression='requestDayOfWeek = :day AND requestTime = :time AND requestEnabled = :enabled',
        ExpressionAttributeValues={
            ':day': current_day,
            ':time': current_time,
            ':enabled': True
        }
    )
    
    # 一致する設定ごとに処理を実行
    for item in response['Items']:
        members = response['Items']
        # ここで実際の処理を呼び出す（例：別のLambda関数を呼び出す）
        invoke_processing_lambda(item['organization_id'])

def invoke_processing_lambda(organization_id):
    lambda_client = boto3.client('lambda')
    lambda_client.invoke(
        FunctionName=f'{stage}-schedule',
        InvocationType='Event',
        Payload=json.dumps({'organization_id': organization_id})
    )

# 処理実行関数
def processing_handler(event, context):
    organization_id = event['organization_id']
    # ここでスケジュールIDに基づいた実際の処理を実行
    print(f"Processing task for organization ID: {organization_id}")
    # 実際の処理をここに実装
    org = get_organization(organization_id)
    response = members_table.query(
        IndexName='OrganizationIndex',
        KeyConditionExpression=Key('organizationId').eq(organization_id)
    )
    send_request_mail(org, response['Items'])

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

def send_request_mail(organization, members):
    organization_id = organization['organization_id']
    reportWeek = organization['reportWeek']

    tz = pytz.timezone(TIMEZONE)
    now = datetime.now(tz)
    weekString = get_string_from_week(now, reportWeek)

    for m in members:
        sendTo = m.get("email")
        sendFrom = common.publisher.get_from_address(organization)
        subject = "【週次報告システム】週次報告をお願いします"
        bodyText = "お疲れさまです。\n下記リンクより週次報告をお願いします。\n"
        link = generate_report_link(organization_id, m["memberUuid"], weekString)
        common.publisher.send_mail(sendFrom, sendTo, subject, bodyText + link)

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
    # 日付オブジェクトに変換（文字列が渡された場合に対応）
    if isinstance(current_date, str):
        current_date = datetime.datetime.strptime(current_date, "%Y-%m-%d").date()
    elif isinstance(current_date, datetime.datetime):
        current_date = current_date.date()
    
    # オフセットを適用
    current_date += datetime.timedelta(weeks=week_offset)
    
    # 木曜日に移動（ISO 8601準拠）
    thursday = current_date + datetime.timedelta(days=(3 - current_date.weekday() + 7) % 7)
    
    # その年の最初の木曜日を計算
    first_thursday = datetime.date(thursday.year, 1, 1)
    if first_thursday.weekday() != 3:
        first_thursday = first_thursday + datetime.timedelta(days=(3 - first_thursday.weekday() + 7) % 7)
    
    # 週番号を計算
    week_number = (thursday - first_thursday).days // 7 + 1
    
    # 結果の文字列を生成
    return f"{thursday.year}-W{week_number:02d}"