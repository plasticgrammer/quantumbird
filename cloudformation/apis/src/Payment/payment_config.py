import os

class PaymentConfig:
    # Stripe関連
    API_KEY = os.environ['STRIPE_SECRET_KEY']
    CURRENCY = 'jpy'
    BILLING_INTERVAL = 'month'
    API_VERSION = '2023-10-16'

    # 環境設定
    STAGE_TO_ENV_MAP = {
        'dev': 'development',
        'prod': 'production'
    }
    ENVIRONMENT = STAGE_TO_ENV_MAP.get(os.environ.get('STAGE', 'dev'), 'development')

    # 環境別のStripe ID設定
    STRIPE_IDS = {
        'development': {
            'pro_price': 'price_1QfZi4LTUjsrHeIRRxB9l122',
            'business_price': 'price_1QfZmFLTUjsrHeIRcjb6Ghyw',
            'business_product': 'prod_RYhAFARRl7RGaB'
        },
        'production': {
            'pro_price': 'price_1QfbHxLTUjsrHeIRh22xGDtJ',
            'business_price': 'price_1QfbJALTUjsrHeIRCQ8ll7nd',
<<<<<<< HEAD
            'business_product': 'prod_RYijnwpMJlZH7n'
=======
            'business_product': 'prod_RYikjB8getMLbp'
>>>>>>> c6ab7804d6aab61f95be304a2c60f8ab5c9a6854
        }
    }

    # プラン関連
    PRICE_ID_FREE = 'price_free'
    PRICE_ID_PRO = STRIPE_IDS[ENVIRONMENT]['pro_price']
    PRICE_ID_BUSINESS = STRIPE_IDS[ENVIRONMENT]['business_price']
    PRODUCT_ID_BUSINESS = STRIPE_IDS[ENVIRONMENT]['business_product']
    VALID_PRICE_IDS = [PRICE_ID_FREE, PRICE_ID_PRO, PRICE_ID_BUSINESS]

    # プラン設定
    PRICE_TO_PLAN_MAP = {
        PRICE_ID_FREE: 'free',
        PRICE_ID_PRO: 'pro',
        PRICE_ID_BUSINESS: 'business'
    }
    PLAN_TO_PRICE_MAP = {v: k for k, v in PRICE_TO_PLAN_MAP.items()}

    # 料金関連
    BUSINESS_BASE_PRICE = 2000
    BUSINESS_PER_ACCOUNT_PRICE = 500

    # 時間関連
    SECONDS_PER_DAY = 24 * 3600
    DAYS_IN_MONTH = 30
    PLAN_CHANGE_COOLDOWN_SECONDS = 24 * 3600
    REACTIVATION_WINDOW_SECONDS = 48 * 3600
    IDEMPOTENCY_KEY_TTL = 24 * 3600

    # カードエラーメッセージ
    CARD_ERROR_MESSAGES = {
        'card_declined': '決済が拒否されました。',
        'expired_card': 'カードの有効期限が切れています。',
        'incorrect_cvc': 'セキュリティコードが正しくありません。',
        'processing_error': '決済処理中にエラーが発生しました。',
        'incorrect_number': 'カード番号が正しくありません。',
        'invalid_expiry_month': '有効期限の月が無効です。',
        'invalid_expiry_year': '有効期限の年が無効です。'
    }

    # レスポンスメッセージ
    RESPONSE_MESSAGES = {
        'subscription_created': 'サブスクリプションが正常に作成されました',
        'free_plan_selected': 'フリープランが選択されました',
        'plan_changed': 'プランが正常に変更されました',
        'changed_to_free': 'フリープランに変更されました',
        'account_count_updated': 'アカウント数が正常に更新されました',
        'payment_method_updated': '支払い方法が正常に更新されました',
        'invalid_plan_id': '無効なプランIDです',
        'system_error': 'システムエラーが発生しました。管理者に連絡してください。',
        'method_not_allowed': 'POSTメソッドのみ許可されています',
        'endpoint_not_found': '指定されたエンドポイントは存在しません',
        'invalid_json': '無効なJSONフォーマットです',
        'missing_parameter': '{field}は必須パラメータです'
    }

    # Stripe APIデフォルトパラメータ
    DEFAULT_STRIPE_PARAMS = {
        'stripe_version': API_VERSION
    }

    # HTTP関連メッセージ
    HTTP_MESSAGES = {
        'method_not_allowed': RESPONSE_MESSAGES['method_not_allowed'],
        'endpoint_not_found': RESPONSE_MESSAGES['endpoint_not_found']
    }

    # ログメッセージ
    LOG_MESSAGES = {
        'payment_error': '決済エラー: %s',
        'system_error': 'システムエラー: %s',
        'request_start': 'リクエスト開始: %s'
    }