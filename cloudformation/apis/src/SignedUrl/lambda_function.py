import json
import os
import time
import hmac
import hashlib
from base64 import urlsafe_b64encode, urlsafe_b64decode
import pytz
from datetime import datetime, timedelta

# 環境変数から秘密鍵とタイムゾーンを取得
SECRET_KEY = os.environ['SECRET_KEY'].encode('utf-8')
TIMEZONE = os.environ.get('TIMEZONE', 'UTC')

def lambda_handler(event, context):
    http_method = event['httpMethod']
    
    if http_method == 'GET':
        if event['path'] == '/generate-url':
            return generate_signed_url(event)
        else:
            return validate_and_serve_content(event)
    else:
        return create_response(405, "Method Not Allowed")

def generate_signed_url(event):
    query_params = event.get('queryStringParameters', {}) or {}
    page_path = query_params.get('path', '')
    validity_minutes = int(query_params.get('validity', '60'))  # デフォルトは60分
    
    tz = pytz.timezone(TIMEZONE)
    current_time = datetime.now(tz)
    expiration_time = current_time + timedelta(minutes=validity_minutes)
    expiration_timestamp = int(expiration_time.timestamp())
    
    to_sign = f"{page_path}:{expiration_timestamp}".encode('utf-8')
    signature = hmac.new(SECRET_KEY, to_sign, hashlib.sha256).digest()
    encoded_signature = urlsafe_b64encode(signature).decode('utf-8').rstrip('=')
    
    signed_url = f"https://{event['headers']['Host']}{page_path}?exp={expiration_timestamp}&sig={encoded_signature}"
    
    return create_response(200, {
        'signedUrl': signed_url,
        'expirationTime': expiration_time.isoformat(),
        'timezone': TIMEZONE
    })

def validate_and_serve_content(event):
    query_params = event.get('queryStringParameters', {}) or {}
    if not query_params or 'exp' not in query_params or 'sig' not in query_params:
        return create_response(400, "Missing required parameters")

    path = event['path']
    expiration = query_params['exp']
    provided_signature = query_params['sig']

    # 署名を検証
    to_sign = f"{path}:{expiration}".encode('utf-8')
    expected_signature = hmac.new(SECRET_KEY, to_sign, hashlib.sha256).digest()
    expected_signature_encoded = urlsafe_b64encode(expected_signature).decode('utf-8').rstrip('=')

    if not hmac.compare_digest(provided_signature, expected_signature_encoded):
        return create_response(403, "Invalid signature")

    # 有効期限を検証
    current_time = int(time.time())
    if current_time > int(expiration):
        return create_response(403, "URL has expired")

    # プロテクトされたコンテンツを返す
    protected_content = get_protected_content(path)
    return create_response(200, protected_content)

def create_response(status_code, body):
    return {
        'statusCode': status_code,
        'body': json.dumps(body),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'  # CORS設定
        }
    }

def get_protected_content(path):
    # この関数は実際のプロテクトされたコンテンツを取得または生成します
    # 例として、パスに基づいて簡単なメッセージを返します
    return f"This is protected content for path: {path}"