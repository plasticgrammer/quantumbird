import json
import logging
import boto3
from boto3.dynamodb.conditions import Key
import os

print('Loading function')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
stage = os.environ.get('STAGE', 'dev')
table_name = f'{stage}-WeeklyReports'
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")
    try:
        # Check if the event has a 'body' key (API Gateway) or is the body itself (direct invocation)
        if 'body' in event:
            report_data = json.loads(event['body'])
        else:
            report_data = event

        # Extract report details
        member_uuid = report_data.get('memberUuid')
        week_string = report_data.get('weekString')
        organization_id = report_data.get('organizationId')
        accomplishments = report_data.get('accomplishments')
        next_week_plans = report_data.get('nextWeekPlans')
        blockers = report_data.get('blockers')
        
        # Prepare the item to be inserted
        item = {
            'memberUuid': member_uuid,
            'weekString': week_string,
            'organizationId': organization_id,
            'accomplishments': accomplishments,
            'nextWeekPlans': next_week_plans,
            'blockers': blockers
        }
        
        # Insert or update the item in DynamoDB
        response = table.put_item(Item=item)
        logger.info(f"DynamoDB response: {response}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps('Weekly report saved successfully!')
        }
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps(f'Error saving weekly report: {str(e)}')
        }

def get_reports_by_organization(organization_id, week_string):
    try:
        response = table.query(
            IndexName='OrganizationWeekIndex',
            KeyConditionExpression=Key('organizationId').eq(organization_id) & Key('weekString').eq(week_string)
        )
        return response['Items']
    except Exception as e:
        print(f"Error querying reports: {str(e)}")
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
        print(f"Error getting report: {str(e)}")
        raise e