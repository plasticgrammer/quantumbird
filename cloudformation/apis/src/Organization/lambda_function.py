import json
import logging
import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal
import os
import uuid
import common.publisher

print('Loading function')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
stage = os.environ.get('STAGE', 'dev')
organizations_table_name = f'{stage}-Organizations'
members_table_name = f'{stage}-Members'
organizations_table = dynamodb.Table(organizations_table_name)
members_table = dynamodb.Table(members_table_name)

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

        if http_method in ['GET', 'get']:
            return handle_get(event)
        elif http_method in ['POST', 'create']:
            return handle_post(event)
        elif http_method in ['PUT', 'update']:
            return handle_put(event)
        elif http_method in ['DELETE', 'delete']:
            return handle_delete(event)
        else:
            return create_response(400, f'Unsupported operation: {http_method}')
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return create_response(500, f'Internal server error: {str(e)}')

def handle_get(event):
    params = event.get('queryStringParameters') or event.get('payload') or {}
    if not params:
        return create_response(400, 'Missing query parameters')

    if 'organizationId' in params:
        org = get_organization(params['organizationId'])
        if org is None:
            return create_response(404, f"Organization with id {params['organizationId']} not found")
        members = list_members(params['organizationId'])
        org['members'] = sorted(members, key=lambda x: x.get('id', ''))  # IDでソート
        return create_response(200, org)
    elif 'memberUuid' in params:
        member = get_member(params['memberUuid'])
        if member is None:
            return create_response(404, f"Member with uuid {params['memberUuid']} not found")
        return create_response(200, member)
    else:
        orgs = list_organizations()
        return create_response(200, orgs)

def handle_post(event):
    data = parse_body(event)
    if 'organizationId' in data:
        item = prepare_organization_item(data)
        response = organizations_table.put_item(Item=item)
        logger.info(f"DynamoDB response: {response}")
        return create_response(201, 'Organization created successfully')
    elif 'memberUuid' in data:
        item = prepare_member_item(data)
        response = members_table.put_item(Item=item)
        logger.info(f"DynamoDB response: {response}")
        return create_response(201, 'Member created successfully')
    else:
        return create_response(400, 'Invalid data structure')

def handle_put(event):
    data = parse_body(event)
    if 'organizationId' in data:
        # 組織情報の更新
        org_item = prepare_organization_item(data)
        response = organizations_table.put_item(Item=org_item)
        logger.info(f"Organization update response: {response}")

        # メンバー情報の更新
        if 'members' in data:
            update_members(data['organizationId'], data['members'])

        return create_response(200, 'Organization and members updated successfully')
    elif 'memberUuid' in data:
        existing_member = get_member(data['memberUuid'])
        item = prepare_member_item(data, existing_member)
        response = members_table.put_item(Item=item)
        logger.info(f"Member update response: {response}")
        return create_response(200, 'Member updated successfully')
    else:
        return create_response(400, 'Invalid data structure')

def handle_delete(event):
    params = event.get('queryStringParameters') or event.get('payload') or {}
    if 'organizationId' in params:
        delete_organization_and_members(params['organizationId'])
        return create_response(200, 'Organization and its members deleted successfully')
    elif 'memberUuid' in params:
        delete_member(params['memberUuid'])
        return create_response(200, 'Member deleted successfully')
    else:
        return create_response(400, 'Missing required parameters')

def parse_body(event):
    if 'body' in event:
        return json.loads(event['body'])
    elif 'payload' in event:
        return event['payload']
    else:
        return event

def prepare_organization_item(org_data):
    return {
        'organizationId': org_data.get('organizationId'),
        'name': org_data.get('name'),
        'sender': org_data.get('sender'),
        'requestEnabled': org_data.get('requestEnabled'),
        'requestTime': org_data.get('requestTime'),
        'requestDayOfWeek': org_data.get('requestDayOfWeek'),
        'reportWeek': org_data.get('reportWeek')
    }

def prepare_member_item(member_data, existing_member=None):
    if existing_member is None:
        existing_member = {}
    
    updated_member = {
        'memberUuid': member_data.get('memberUuid', existing_member.get('memberUuid', str(uuid.uuid4()))),
        'id': member_data.get('id', existing_member.get('id')),
        'organizationId': member_data.get('organizationId', existing_member.get('organizationId')),
        'name': member_data.get('name', existing_member.get('name')),
        'email': member_data.get('email', existing_member.get('email')),
        'projects': member_data.get('projects', existing_member.get('projects', []))
    }
    return {k: v for k, v in updated_member.items() if v is not None}

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

def list_organizations():
    try:
        response = organizations_table.scan()
        return response['Items']
    except Exception as e:
        logger.error(f"Error listing organizations: {str(e)}", exc_info=True)
        raise e

def list_members(organization_id):
    try:
        response = members_table.query(
            IndexName='OrganizationIndex',
            KeyConditionExpression=Key('organizationId').eq(organization_id)
        )
        members = response['Items']
        # IDの昇順でソート
        sorted_members = sorted(members, key=lambda x: x.get('id', ''))
        return sorted_members
    except Exception as e:
        logger.error(f"Error listing members: {str(e)}", exc_info=True)
        raise e

def update_members(organization_id, members):
    org = get_organization(organization_id)

    # 既存のメンバーを取得
    existing_members = list_members(organization_id)
    existing_members_dict = {m['id']: m for m in existing_members if 'id' in m}

    # メンバーの更新と追加
    for member in members:
        existing_member = existing_members_dict.get(member.get('id'))
        member_item = prepare_member_item(member, existing_member)
        if existing_member is None:
            try:
                send_registor_mail(org, member_item)
            except Exception as e:
                logger.error(f"Failed to send registration email to member {member_item.get('id')}: {str(e)}")

        member_item['organizationId'] = organization_id
        members_table.put_item(Item=member_item)
        if member.get('id') in existing_members_dict:
            del existing_members_dict[member.get('id')]

    # 削除されたメンバーの処理
    for member_id in existing_members_dict:
        delete_member_by_id(organization_id, member_id)

def send_registor_mail(organization, member):
    sendFrom = common.publisher.get_from_address(organization)
    subject = "【週次報告システム】メンバー登録設定完了のご連絡"
    bodyText = "「週次報告システム」の送信先に登録されました。\n※本メールは、登録した際に配信される自動配信メールです。\n"
    # Check if email exists and is not None
    if member.get('email'):
        common.publisher.send_mail(sendFrom, [member['email']], subject, bodyText)
    else:
        logger.warning(f"No email address found for member: {member.get('id', 'Unknown ID')}")

def delete_organization_and_members(organization_id):
    try:
        # Delete organization
        organizations_table.delete_item(
            Key={
                'organizationId': organization_id
            }
        )
        
        # Delete all members of the organization
        members = list_members(organization_id)
        with members_table.batch_writer() as batch:
            for member in members:
                batch.delete_item(
                    Key={
                        'memberUuid': member['memberUuid']
                    }
                )
    except Exception as e:
        logger.error(f"Error deleting organization and members: {str(e)}", exc_info=True)
        raise e

def delete_member(member_uuid):
    try:
        members_table.delete_item(
            Key={
                'memberUuid': member_uuid
            }
        )
    except Exception as e:
        logger.error(f"Error deleting member: {str(e)}", exc_info=True)
        raise e

def delete_member_by_id(organization_id, member_id):
    # IDとorganizationIdを使用してmemberUuidを検索
    response = members_table.query(
        IndexName='OrganizationIndex',
        KeyConditionExpression=Key('organizationId').eq(organization_id),
        FilterExpression=Key('id').eq(member_id)
    )
    
    items = response.get('Items', [])
    if items:
        member_uuid = items[0]['memberUuid']
        members_table.delete_item(Key={'memberUuid': member_uuid})

def create_response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
        },
        'body': body
    }