import datetime
import json
import urllib.parse
from decimal import Decimal

def parse_body(operation, event):
    """リクエストを解析してJson形式で返します
    """
    contentType = 'unknown'
    if event['headers']:
        if ('content-type' in event['headers']):
            contentType = event['headers']['content-type'] 
        elif ('Content-Type' in event['headers']):  # 古いWindows&IEだとキャメルケースになる
            contentType = event['headers']['Content-Type'] 
    
    if contentType.startswith('application/json'):
        payload = json.loads(event['body'])
    else:
        payload = event['queryStringParameters'] if operation == 'GET' else dict(urllib.parse.parse_qsl(event['body']))
    return payload

def respond(err, res=None):
    """Lambdaの戻り値(Json)を構築して返します
    """
    return {
        'isBase64Encoded': False,
        'statusCode': '400' if err else '200',
        'body': err.args[0] if err else json.dumps(res, default=decimal_default_proc),
        'headers': {
            'Access-Control-Allow-Origin' : '*',
            'Access-Control-Allow-Methods': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Content-Type': 'application/json'
        },
    }

def timestamp():
    """タイムスタンプを返します
    """
    dt = datetime.datetime.now()
    return dt.strftime("%Y%m%d%H%M%S%f")

def decimal_default_proc(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def dict_filter(map, keys):
    return {k:map[k] for k in map.keys() if k in keys}

def strtobool(val):
    """Convert a string representation of truth to bool

    True values are 'y', 'yes', 't', 'true', 'on', and '1'
    False values are 'n', 'no', 'f', 'false', 'off', and '0'
    Raises ValueError if 'val' is anything else.
    """
    val = str(val).lower()
    if val in ('y', 'yes', 't', 'true', 'on', '1'):
        return True
    elif val in ('n', 'no', 'f', 'false', 'off', '0'):
        return False
    else:
        raise ValueError(f"Invalid truth value {val}")