from typing import Dict, Any, Optional, Callable
import json
import logging
import traceback
from common.exception import ApplicationException
from decimal import Decimal

logger = logging.getLogger()

def create_response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
        },
        'body': json.dumps(body, default=decimal_default_proc)
    }

def decimal_default_proc(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def validate_required_params(data: Dict[str, Any], required_fields: list) -> None:
    """必須パラメータの検証"""
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        raise ApplicationException(400, f"Required fields missing: {', '.join(missing_fields)}")

def parse_request_body(event: Dict[str, Any]) -> Dict[str, Any]:
    """リクエストボディのパース"""
    try:
        if 'body' not in event:
            return {}
        return json.loads(event['body']) if event['body'] else {}
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse request body: {e}")
        raise ApplicationException(400, "Invalid JSON in request body")

def get_query_param(event: Dict[str, Any], param_name: str) -> Optional[str]:
    """クエリパラメータの取得"""
    params = event.get('queryStringParameters', {}) or {}
    return params.get(param_name)

def handle_lambda_errors(func: Callable) -> Callable:
    """Lambda関数のエラーハンドリングデコレータ"""
    def wrapper(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
        try:
            return func(event, context)
        except ApplicationException as e:
            logger.warning(f"Application error: {str(e)}")
            return create_api_response(e.status_code, {'error': str(e)})
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            logger.error(traceback.format_exc())
            return create_api_response(500, {'error': 'Internal Server Error'})
    return wrapper