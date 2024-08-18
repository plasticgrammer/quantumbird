# スケジューラー関数
import boto3
import logging
import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from boto3.dynamodb.conditions import Key

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 環境変数TZからタイムゾーンを取得
TIMEZONE = ZoneInfo(os.environ.get('TZ', 'UTC'))
stage = os.environ.get('STAGE', 'dev')

dynamodb = boto3.resource('dynamodb')
organizations_table_name = f'{stage}-Organizations'
members_table_name = f'{stage}-Members'
organizations_table = dynamodb.Table(organizations_table_name)
members_table = dynamodb.Table(members_table_name)

# 数値の曜日を文字列に変換する辞書
DAY_OF_WEEK = {
    0: 'monday',
    1: 'tuesday',
    2: 'wednesday',
    3: 'thursday',
    4: 'friday',
    5: 'saturday',
    6: 'sunday'
}

def lambda_handler(event, context):
    # 現在の曜日と時間を取得
    now = datetime.now(TIMEZONE)
    current_day = DAY_OF_WEEK[now.weekday()]
    current_time = f"{now.hour:02d}:00"
    logger.info(f"Filter by requestDayOfWeek = {current_day} AND requestTime = {current_time}")
    
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
        invoke_processing_lambda(item['organizationId'])

def invoke_processing_lambda(organization_id):
    lambda_client = boto3.client('lambda')
    payload = json.dumps({
        'payload': {
            'organization_id': organization_id
        }
    })
    logger.info(f"Invoking Lambda with payload: {payload}")
    try:
        response = lambda_client.invoke(
            FunctionName=f'{stage}-send-request',
            InvocationType='Event',
            Payload=payload
        )
        logger.info(f"Lambda invocation response: {response}")
        
        # レスポンスのステータスコードを確認
        if response['StatusCode'] != 202:
            logger.error(f"Unexpected status code: {response['StatusCode']}")
    except Exception as e:
        logger.error(f"Error invoking Lambda: {str(e)}", exc_info=True)