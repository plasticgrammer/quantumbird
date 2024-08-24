import os
import boto3
import json
import logging
import jwt
from datetime import datetime, timedelta, timezone
import base64
import struct

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_secret():
    ssm = boto3.client('ssm')
    parameter_name = os.environ['JWT_SECRET_PARAMETER']
    response = ssm.get_parameter(Name=parameter_name, WithDecryption=True)
    return response['Parameter']['Value']

def generate_short_token(event):
    data = parse_body(event)
    logger.info(f"Parsed data for token generation: {json.dumps(data)}")
    
    if 'organizationId' not in data or 'weekString' not in data:
        logger.error("Missing required fields in the request")
        return create_response(400, 'Missing required fields: organizationId or weekString')
    
    secret = get_secret()
    
    # 現在時刻からUNIXタイムスタンプ（秒）を取得
    now = int(datetime.now(timezone.utc).timestamp())
    # 有効期限を24時間後に設定
    exp = now + 24 * 60 * 60
    
    # ペイロードを短い形式にエンコード
    payload = struct.pack('>I', exp) + data['organizationId'].encode() + b'\0' + data['weekString'].encode()
    
    # JWTの代わりに、単純な署名付きトークンを生成
    signature = jwt.encode({'payload': base64.urlsafe_b64encode(payload).decode()}, secret, algorithm='HS256')
    
    # Base64URLエンコードされたペイロードと署名の最初の16文字を組み合わせて短いトークンを生成
    short_token = base64.urlsafe_b64encode(payload).decode().rstrip('=') + '.' + signature[:16]
    
    return create_response(200, {'token': short_token})

def verify_short_token(event):
    data = parse_body(event)
    logger.info(f"Parsed data for token verification: {json.dumps(data)}")
    
    if 'token' not in data:
        logger.error("Missing token in the request")
        return create_response(400, 'Missing token')
    
    secret = get_secret()
    try:
        # トークンを分割
        payload_b64, signature_part = data['token'].split('.')
        
        # Base64デコード（パディングを追加）
        payload = base64.urlsafe_b64decode(payload_b64 + '==')
        
        # ペイロードを解析
        exp = struct.unpack('>I', payload[:4])[0]
        org_id, week_string = payload[4:].split(b'\0')
        
        # 有効期限をチェック
        if exp < datetime.now(timezone.utc).timestamp():
            raise jwt.ExpiredSignatureError("Token has expired")
        
        # 署名を検証
        full_signature = jwt.encode({'payload': payload_b64}, secret, algorithm='HS256')
        if full_signature[:16] != signature_part:
            raise jwt.InvalidTokenError("Invalid token")
        
        # デコードされたデータを返す
        decoded_data = {
            'organizationId': org_id.decode(),
            'weekString': week_string.decode(),
            'exp': datetime.fromtimestamp(exp, tz=timezone.utc).isoformat()  # ISO形式の文字列に変換
        }
        logger.info(f"Decoded token data: {json.dumps(decoded_data)}")
        return create_response(200, decoded_data)
    
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        return create_response(400, 'Token has expired')
    except (jwt.InvalidTokenError, ValueError, struct.error):
        logger.warning("Invalid token")
        return create_response(400, 'Invalid token')

def lambda_handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")
    try:
        if 'httpMethod' in event:
            http_method = event['httpMethod']
        elif 'operation' in event:
            http_method = event['operation']
        else:
            logger.error("Invalid event structure")
            return create_response(400, 'Invalid event structure')

        if http_method == 'generateToken':
            return generate_short_token(event)
        elif http_method == 'verifyToken':
            return verify_short_token(event)
        else:
            logger.error(f"Unsupported HTTP method: {http_method}")
            return create_response(400, f'Unsupported HTTP method: {http_method}')
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return create_response(500, f'Internal server error: {str(e)}')

def parse_body(event):
    if 'body' in event:
        try:
            return json.loads(event['body'])
        except json.JSONDecodeError:
            logger.error("Failed to parse JSON body")
            return {}
    elif 'payload' in event:
        return event['payload']
    else:
        logger.warning("No body or payload found in event")
        return event

def create_response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            "content-type":"application/json",
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
        },
        'body': body
    }