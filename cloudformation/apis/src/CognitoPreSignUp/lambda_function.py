import boto3
import os
from botocore.exceptions import ClientError

cognito_idp = boto3.client('cognito-idp')
USER_POOL_ID = os.environ['USER_POOL_ID']

def lambda_handler(event, context):
    try:
        # カスタム属性から組織IDを取得
        organization_id = event['request']['userAttributes'].get('custom:organizationId')

        if not organization_id:
            raise ValueError("組織IDが提供されていません。")

        # Cognitoユーザープールで組織IDの重複をチェック
        response = cognito_idp.list_users(
            UserPoolId=USER_POOL_ID,
            Filter=f'custom:organizationId = "{organization_id}"'
        )

        if len(response['Users']) > 0:
            raise ValueError("この組織IDは既に使用されています。")

        # 重複がない場合、サインアッププロセスを続行
        print(f"組織ID {organization_id} は使用可能です。サインアッププロセスを続行します。")
        return event

    except ClientError as e:
        print(f"Cognito APIエラー: {str(e)}")
        raise e
    except ValueError as e:
        print(f"バリデーションエラー: {str(e)}")
        raise e
    except Exception as e:
        print(f"予期しないエラー: {str(e)}")
        raise e