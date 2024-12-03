import uuid
import time
from decimal import Decimal

def float_to_decimal(obj):
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: float_to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [float_to_decimal(v) for v in obj]
    return obj

def prepare_weekly_report_item(report_data, existing_report=None, timezone=None):
    now = datetime.now(timezone) if timezone else datetime.utcnow()
    current_time = now.isoformat()

    item = {
        'memberUuid': report_data.get('memberUuid'),
        'weekString': report_data.get('weekString'),
        'organizationId': report_data.get('organizationId'),
        'projects': report_data.get('projects'),
        'overtimeHours': float_to_decimal(report_data.get('overtimeHours')),
        'issues': report_data.get('issues'),
        'improvements': report_data.get('improvements'),
        'rating': report_data.get('rating', {}),
        'stressHelp': report_data.get('stressHelp'),
        'status': report_data.get('status'),
        'feedbacks': report_data.get('feedbacks', []),
        'approvedAt': report_data.get('approvedAt'),
        'createdAt': report_data.get('createdAt', current_time)
    }
    
    if existing_report:
        existing_report.update(item)
        return existing_report
    return item

def prepare_member_item(member_data, existing_member=None):
    if existing_member is None:
        existing_member = {}

    updated_member = {
        'memberUuid': member_data.get('memberUuid', existing_member.get('memberUuid', str(uuid.uuid4()))),
        'id': member_data.get('id', existing_member.get('id')),
        'organizationId': member_data.get('organizationId', existing_member.get('organizationId')),
        'name': member_data.get('name', existing_member.get('name')),
        'email': member_data.get('email', existing_member.get('email')),
        'extraInfo': member_data.get('extraInfo', existing_member.get('extraInfo', {})),
        'projects': member_data.get('projects', existing_member.get('projects', [])),
        'adviceTickets': member_data.get('adviceTickets', existing_member.get('adviceTickets', 0))
    }
    return {k: v for k, v in updated_member.items() if v is not None}

def prepare_organization_item(org_data, existing_org=None):
    if existing_org is None:
        existing_org = {}
    
    # 既存のfeaturesを保持
    features = existing_org.get('features', {}).copy()
    
    # 新しいfeaturesがある場合は更新
    if 'features' in org_data:
        features.update(org_data['features'])
    
    updated_org = {
        'organizationId': org_data.get('organizationId', existing_org.get('organizationId')),
        'name': org_data.get('name', existing_org.get('name')),
        'sender': org_data.get('sender', existing_org.get('sender')),
        'senderName': org_data.get('senderName', existing_org.get('senderName')),
        'requestEnabled': org_data.get('requestEnabled', existing_org.get('requestEnabled')),
        'requestTime': org_data.get('requestTime', existing_org.get('requestTime')),
        'requestDayOfWeek': org_data.get('requestDayOfWeek', existing_org.get('requestDayOfWeek')),
        'reportWeek': org_data.get('reportWeek', existing_org.get('reportWeek')),
        'features': features,
        'adminSubscriptions': existing_org.get('adminSubscriptions', {})
    }
    
    if 'adminSubscriptions' in org_data:
        updated_org['adminSubscriptions'].update(org_data['adminSubscriptions'])

    return {k: v for k, v in updated_org.items() if v is not None}

def prepare_task_item(user_id, task_data, existing_task=None, timezone=None):
    now = datetime.now(timezone) if timezone else datetime.utcnow()
    current_time = now.isoformat()
    
    updated_task = {
        'userId': user_id,
        'taskId': task_data.get('taskId', existing_task.get('taskId', str(uuid.uuid4()))),
        'title': task_data.get('title', existing_task.get('title')),
        'completed': task_data.get('completed', existing_task.get('completed', False)),
        'createdAt': existing_task.get('createdAt', current_time),
        'updatedAt': current_time
    }
    return {k: v for k, v in updated_task.items() if v is not None}