# スケジューラー関数
import boto3
import json
import os
import pytz
from datetime import datetime

TIMEZONE = os.environ.get('TIMEZONE', 'UTC')

dynamodb = boto3.resource('dynamodb')
stage = os.environ.get('STAGE', 'dev')
organizations_table_name = f'{stage}-Organizations'
organizations_table = dynamodb.Table(organizations_table_name)

def scheduler_handler(event, context):
    
    # 現在の曜日と時間を取得
    tz = pytz.timezone(TIMEZONE)
    now = datetime.now(tz)
    current_day = now.weekday()
    current_time = now.strftime("%H:%M")
    
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
        invoke_processing_lambda(item['ID'])

def invoke_processing_lambda(schedule_id):
    lambda_client = boto3.client('lambda')
    lambda_client.invoke(
        FunctionName='processing_function_name',
        InvocationType='Event',
        Payload=json.dumps({'schedule_id': schedule_id})
    )

# 処理実行関数
def processing_handler(event, context):
    schedule_id = event['schedule_id']
    # ここでスケジュールIDに基づいた実際の処理を実行
    print(f"Processing task for schedule ID: {schedule_id}")
    # 実際の処理をここに実装