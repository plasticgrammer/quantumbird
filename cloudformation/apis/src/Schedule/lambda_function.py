# スケジューラー関数
import boto3
import logging
import json
import os
import urllib.parse
from datetime import datetime
from zoneinfo import ZoneInfo
from boto3.dynamodb.conditions import Key
import common.publisher

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 環境変数TZからタイムゾーンを取得
TIMEZONE = ZoneInfo(os.environ.get('TZ', 'UTC'))
BASE_URL = os.environ.get('BASE_URL', 'http://localhost:3000')
stage = os.environ.get('STAGE', 'dev')

dynamodb = boto3.resource('dynamodb')
organizations_table_name = f'{stage}-Organizations'
members_table_name = f'{stage}-Members'
organizations_table = dynamodb.Table(organizations_table_name)
members_table = dynamodb.Table(members_table_name)

def scheduler_handler(event, context):
    # 現在の曜日と時間を取得
    now = datetime.now(TIMEZONE)
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
        # ここで実際の処理を呼び出す（例：別のLambda関数を呼び出す）
        invoke_processing_lambda(item['organization_id'])

def invoke_processing_lambda(organization_id):
    lambda_client = boto3.client('lambda')
    payload = json.dumps({
        'detail-type': 'CustomInvoke',
        'payload': {
            'organization_id': organization_id
        }
    })
    logger.info(f"Invoking Lambda with payload: {payload}")
    try:
        response = lambda_client.invoke(
            FunctionName=f'{stage}-schedule',
            InvocationType='Event',
            Payload=payload
        )
        logger.info(f"Lambda invocation response: {response}")
        
        # レスポンスのステータスコードを確認
        if response['StatusCode'] != 202:
            logger.error(f"Unexpected status code: {response['StatusCode']}")
    except Exception as e:
        logger.error(f"Error invoking Lambda: {str(e)}", exc_info=True)

# 処理実行関数
def lambda_handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")
    logger.info(f"Event type: {type(event)}")
    try:
        organization_id = None
        if isinstance(event, dict):
            payload = event.get('payload', {})
            if isinstance(payload, str):
                payload = json.loads(payload)
            elif isinstance(payload, dict):
                organization_id = payload.get('organization_id')
            if not organization_id:
                organization_id = event.get('organization_id')
        elif isinstance(event, str):
            event_dict = json.loads(event)
            payload = event_dict.get('payload', {})
            if isinstance(payload, dict):
                organization_id = payload.get('organization_id')
            if not organization_id:
                organization_id = event_dict.get('organization_id')

        if not organization_id:
            raise ValueError("organization_id not found in the event")

        logger.info(f"Processing task for organization ID: {organization_id}")

        org = get_organization(organization_id)
        if not org:
            raise ValueError(f"Organization not found for ID: {organization_id}")

        response = members_table.query(
            IndexName='OrganizationIndex',
            KeyConditionExpression=Key('organizationId').eq(organization_id)
        )
        send_request_mail(org, response['Items'])

        return {
            'statusCode': 200,
            'body': json.dumps('Processing completed successfully')
        }

    except Exception as e:
        logger.error(f"Error processing event: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error processing event: {str(e)}')
        }
    
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
    organization_id = organization['organizationId']
    reportWeek = organization.get('reportWeek', 0)

    now = datetime.now(TIMEZONE)
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
        current_date = datetime.strptime(current_date, "%Y-%m-%d").replace(tzinfo=TIMEZONE).date()
    elif isinstance(current_date, datetime):
        current_date = current_date.date()
    
    # オフセットを適用
    current_date += datetime.timedelta(weeks=week_offset)
    
    # 木曜日に移動（ISO 8601準拠）
    thursday = current_date + datetime.timedelta(days=(3 - current_date.weekday() + 7) % 7)
    
    # その年の最初の木曜日を計算
    first_thursday = datetime(thursday.year, 1, 1, tzinfo=TIMEZONE).date()
    if first_thursday.weekday() != 3:
        first_thursday = first_thursday + datetime.timedelta(days=(3 - first_thursday.weekday() + 7) % 7)
    
    # 週番号を計算
    week_number = (thursday - first_thursday).days // 7 + 1
    
    # 結果の文字列を生成
    return f"{thursday.year}-W{week_number:02d}"