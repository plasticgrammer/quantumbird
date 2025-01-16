import json
import boto3
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger()
bedrock = boto3.client('bedrock-runtime', region_name="ap-northeast-1")

def invoke_claude(prompt: str) -> str:
    """Claude (Anthropic Claude) を呼び出してアドバイスを生成する"""
    try:
        body = json.dumps({
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 600,
            "temperature": 0.8,
            "top_p": 0.9,
            "top_k": 250,
            "anthropic_version": "bedrock-2023-05-31"
        })

        response = bedrock.invoke_model(
            body=body,
            modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
            contentType="application/json",
            accept="application/json"
        )
        
        response_body = json.loads(response.get('body').read())
        logger.info(f"Claude response: {response_body}")
        return response_body.get('content')[0].get('text', '')
    
    except ClientError as e:
        logger.error(f"Error invoking Bedrock: {str(e)}")
        raise Exception("アドバイスの生成中にエラーが発生しました。")
