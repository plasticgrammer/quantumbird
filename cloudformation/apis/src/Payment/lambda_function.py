import json
import stripe
import os
import time
from typing import Dict, Any
from common.utils import create_response

# 定数のグループ化
class PaymentConfig:
    # Stripe関連
    API_KEY = os.environ['STRIPE_SECRET_KEY']
    CURRENCY = 'jpy'
    BILLING_INTERVAL = 'month'

    # プラン関連
    PRICE_ID_FREE = 'price_free'
    PRICE_ID_PRO = 'price_1QJSigJlLYAT4bpznFUNs5eg'
    PRICE_ID_BUSINESS = 'price_1QJSmjJlLYAT4bpzzPjAgcJj'
    PRODUCT_ID_BUSINESS = 'prod_RBqT2Wa1VvXK56'
    VALID_PRICE_IDS = [PRICE_ID_FREE, PRICE_ID_PRO, PRICE_ID_BUSINESS]

    # 料金関連
    BUSINESS_BASE_PRICE = 2000
    BUSINESS_PER_ACCOUNT_PRICE = 500

    # 時間関連
    SECONDS_PER_DAY = 24 * 3600
    DAYS_IN_MONTH = 30
    PLAN_CHANGE_COOLDOWN_SECONDS = 24 * 3600
    REACTIVATION_WINDOW_SECONDS = 48 * 3600

    # planIdとpriceIdのマッピング
    PRICE_TO_PLAN_MAP = {
        PRICE_ID_FREE: 'free',
        PRICE_ID_PRO: 'pro',
        PRICE_ID_BUSINESS: 'business'
    }

# Stripeの設定
stripe.api_key = PaymentConfig.API_KEY

class PaymentError(Exception):
    """支払い処理に関するカスタムエラー"""
    pass

class ResponseMessages:
    """レスポンスメッセージの定数"""
    SUBSCRIPTION_CREATED = 'サブスクリプションが正常に作成されました'
    FREE_PLAN_SELECTED = 'フリープランが選択されました'
    PLAN_CHANGE_SCHEDULED = 'プラン変更が予約されました'
    ACCOUNT_COUNT_UPDATED = 'アカウント数が正常に更新されました'
    PAYMENT_METHOD_UPDATED = '支払い方法が正常に更新されました'

def create_error_response(error: Exception) -> Dict:
    """エラーレスポンスの生成"""
    if isinstance(error, stripe.error.StripeError):
        return create_response(400, {'error': str(error)})
    if isinstance(error, PaymentError):
        return create_response(400, {'error': str(error)})
    return create_response(500, {'error': 'Internal server error'})

def get_or_create_customer(email: str, token: str) -> stripe.Customer:
    """顧客の取得または作成"""
    customers = stripe.Customer.list(email=email, limit=1)
    if customers.data:
        return customers.data[0]
    return stripe.Customer.create(email=email, source=token)

def calculate_business_price(account_count: int) -> int:
    """ビジネスプランの価格計算"""
    return PaymentConfig.BUSINESS_BASE_PRICE + (account_count * PaymentConfig.BUSINESS_PER_ACCOUNT_PRICE)

def create_subscription_response(subscription: Any, price_id: str, account_count: int, message: str = None) -> Dict:
    """統一されたサブスクリプションレスポンスの生成"""
    # priceIdからplanIdへの変換を修正
    plan_id = PaymentConfig.PRICE_TO_PLAN_MAP.get(price_id, 'free')
    
    customer_id = getattr(subscription, 'customer', None)
    
    print(f"Debug - create_subscription_response: price_id={price_id}, plan_id={plan_id}")  # デバッグログ追加
    
    return {
        'message': message or ResponseMessages.SUBSCRIPTION_CREATED,
        'subscription': {
            'id': getattr(subscription, 'id', 'free'),
            'planId': plan_id,
            'priceId': price_id,
            'accountCount': account_count,
            'status': getattr(subscription, 'status', 'active'),
            'currentPeriodEnd': getattr(subscription, 'current_period_end', None),
            'stripeCustomerId': customer_id
        }
    }

def check_plan_change_cooldown(subscription: stripe.Subscription) -> None:
    """プラン変更のクールダウンチェック"""
    if subscription.metadata.get('last_change_at'):
        last_change = int(subscription.metadata.get('last_change_at'))
        if (time.time() - last_change) < PaymentConfig.PLAN_CHANGE_COOLDOWN_SECONDS:
            raise PaymentError('プラン変更は24時間に1回までです')

def create_subscription(body: Dict) -> Dict:
    """サブスクリプション作成処理"""
    email = body['email']
    token = body.get('token')
    price_id = body['priceId']
    account_count = int(body.get('accountCount', 0))
    customer_id = body.get('customerId')

    # プランIDの検証
    valid_price_ids = PaymentConfig.VALID_PRICE_IDS
    if price_id not in valid_price_ids:
        raise ValueError('無効なプランIDです')

    # 顧客の取得または作成
    if customer_id:
        customer = stripe.Customer.retrieve(customer_id)
    else:
        customer = get_or_create_customer(email, token)
        # Cognitoの更新は不要（フロントエンドで行う）

    # フリープランの場合の処理を修正
    if price_id == PaymentConfig.PRICE_ID_FREE:
        return create_subscription_response(None, PaymentConfig.PRICE_ID_FREE, 0)
    
    try:
        # プランに応じた価格設定とサブスクリプション作成
        if price_id == PaymentConfig.PRICE_ID_BUSINESS:  # ビジネスプラン
            total_price = calculate_business_price(account_count)
            subscription = stripe.Subscription.create(
                customer=customer.id,
                items=[{
                    'price_data': {
                        'currency': PaymentConfig.CURRENCY,
                        'product': PaymentConfig.PRODUCT_ID_BUSINESS,  # 商品IDを直接指定
                        'unit_amount': total_price,
                        'recurring': {'interval': PaymentConfig.BILLING_INTERVAL}
                    }
                }],
                metadata={
                    'account_count': str(account_count),
                    'plan_id': 'business'  # planIdをメタデータに保存
                }
            )
        else:  # プロプラン
            subscription = stripe.Subscription.create(
                customer=customer.id,
                items=[{'price': price_id}],
                metadata={'plan_id': 'pro'}  # planIdをメタデータに保存
            )
        
        return create_subscription_response(subscription, price_id, account_count)
    except Exception as e:
        print(f"Subscription creation error: {e}")
        raise

def update_subscription(body: Dict) -> Dict:
    """サブスクリプション更新処理"""
    new_account_count = int(body.get('newAccountCount', 0))  # 文字列を整数に変換
    subscription_id = body['subscriptionId']

    # サブスクリプションの取得と更新
    subscription = stripe.Subscription.retrieve(subscription_id)
    subscription_item = subscription['items']['data'][0]

    # 新しい金額の計算と更新
    new_price = calculate_business_price(new_account_count)

    # サブスクリプションの更新
    stripe.SubscriptionItem.modify(
        subscription_item.id,
        price_data={
            'currency': PaymentConfig.CURRENCY,
            'product': subscription_item.price.product,
            'unit_amount': new_price,
            'recurring': {'interval': PaymentConfig.BILLING_INTERVAL}
        }
    )

    # メタデータの更新
    stripe.Subscription.modify(
        subscription_id,
        metadata={'account_count': str(new_account_count)}
    )

    updated_subscription = stripe.Subscription.retrieve(subscription_id)

    return {
        'message': 'アカウント数が正常に更新されました',
        'subscription': {
            'id': subscription_id,
            'accountCount': new_account_count,
            'status': updated_subscription.status
        }
    }

def create_free_plan_response(customer_id: str = None) -> Dict:
    """フリープランレスポンスの生成"""
    return {
        'message': 'フリープランが選択されました',
        'subscription': {
            'id': 'free',
            'planId': 'free',  # planIdを明示的に設定
            'price': PaymentConfig.PRICE_ID_FREE,
            'accountCount': 0,
            'status': 'active',
            'stripeCustomerId': customer_id  # 顧客IDを維持
        }
    }

def handle_free_plan_change(subscription: stripe.Subscription, body: Dict) -> Dict:
    """フリープランへの変更処理"""
    # 現在のサブスクリプションをキャンセル
    canceled_subscription = stripe.Subscription.modify(
        subscription.id,
        cancel_at_period_end=True,
        metadata={'last_change_at': str(int(time.time()))}
    )
    
    # 既存の顧客IDを維持してレスポンスを返す
    return {
        'message': 'プラン変更が予約されました',
        'subscription': {
            'id': subscription.id,
            'planId': 'free',  # planIdを明示的に設定
            'price': PaymentConfig.PRICE_ID_FREE,
            'status': 'canceled',
            'currentPeriodEnd': canceled_subscription.current_period_end,
            'stripeCustomerId': subscription.customer,  # 顧客IDを維持
            'cancelAt': canceled_subscription.cancel_at  # キャンセル予定日を追加
        }
    }

def handle_paid_plan_change(subscription: stripe.Subscription, new_price_id: str, new_account_count: int) -> Dict:
    """有料プラン間の変更処理"""
    subscription_item = subscription['items']['data'][0]
    
    # 新しいプランIDを取得
    new_plan_id = PaymentConfig.PRICE_TO_PLAN_MAP.get(new_price_id, 'free')
    
    # 新しいプランの設定
    if new_price_id == PaymentConfig.PRICE_ID_BUSINESS:
        update_params = {
            'price_data': {
                'currency': PaymentConfig.CURRENCY,
                'product': PaymentConfig.PRODUCT_ID_BUSINESS,
                'unit_amount': calculate_business_price(new_account_count),
                'recurring': {'interval': PaymentConfig.BILLING_INTERVAL}
            }
        }
    else:
        update_params = {'price': new_price_id}
    
    # サブスクリプションアイテムの更新
    stripe.SubscriptionItem.modify(subscription_item.id, **update_params)

    # メタデータの更新とキャンセル予定の解除
    updated_subscription = stripe.Subscription.modify(
        subscription.id,
        metadata={
            'account_count': str(new_account_count),
            'last_change_at': str(int(time.time())),
            'plan_id': new_plan_id  # plan_idを更新
        },
        cancel_at_period_end=False
    )
    
    return create_subscription_response(updated_subscription, new_price_id, new_account_count)

def change_subscription_plan(body: Dict) -> Dict:
    """プラン変更処理"""
    subscription_id = body['subscriptionId']
    new_price_id = body['priceId']
    new_account_count = int(body.get('accountCount', 0))
    customer_id = body.get('customerId')  # 既存の顧客IDを受け取る

    # フリープランからの変更の場合
    if subscription_id == PaymentConfig.PRICE_ID_FREE:
        if customer_id:  # 既存の顧客IDがある場合
            return create_subscription({**body, 'customerId': customer_id})
        return create_subscription(body)

    try:
        subscription = stripe.Subscription.retrieve(subscription_id)
        
        # プラン変更ロジック
        if new_price_id == PaymentConfig.PRICE_ID_FREE:
            return handle_free_plan_change(subscription, body)
            
        # フリープラン以外への変更時のみクールダウンチェックを実行
        check_plan_change_cooldown(subscription)
        
        if (subscription['items']['data'][0]['price']['id'] == PaymentConfig.PRICE_ID_BUSINESS and 
              new_price_id == PaymentConfig.PRICE_ID_BUSINESS):
            return update_subscription(body)
        else:
            return handle_paid_plan_change(subscription, new_price_id, new_account_count)

    except stripe.error.InvalidRequestError as e:
        if new_price_id == PaymentConfig.PRICE_ID_FREE:
            return create_free_plan_response(customer_id)  # 顧客IDを渡す
        raise e

def reactivate_subscription(body: Dict) -> Dict:
    """解約後のサブスクリプション再開処理（新規関数）"""
    customer_id = body['customerId']
    price_id = body['priceId']
    
    # 過去のサブスクリプション履歴を確認
    subscriptions = stripe.Subscription.list(
        customer=customer_id,
        status='canceled',
        limit=1
    )
    
    if subscriptions.data:
        old_subscription = subscriptions.data[0]
        reactivation_window = PaymentConfig.REACTIVATION_WINDOW_SECONDS
        if (time.time() - old_subscription.canceled_at) < reactivation_window:
            return create_subscription({
                'email': body['email'],
                'token': body['token'],
                'priceId': price_id,
                'accountCount': body.get('accountCount', 0),
                'billing_cycle_anchor': old_subscription.current_period_end
            })
    
    # 通常の新規サブスクリプション作成
    return create_subscription(body)

def get_payment_methods(body: Dict) -> Dict:
    """支払い方法取得処理"""
    try:
        email = body.get('email')
        if not email:
            return {'data': {'paymentMethods': []}}
        
        customers = stripe.Customer.list(email=email, limit=1)
        if not customers.data:
            return {'data': {'paymentMethods': []}}
        
        payment_methods = stripe.PaymentMethod.list(
            customer=customers.data[0].id,
            type='card'
        )
        
        return {
            'data': {
                'paymentMethods': [{
                    'id': pm.id,
                    'brand': pm.card.brand,
                    'last4': pm.card.last4,
                    'expMonth': pm.card.exp_month,
                    'expYear': pm.card.exp_year
                } for pm in payment_methods.data]
            }
        }
    except Exception as e:
        return {'data': {'paymentMethods': []}, 'error': str(e)}

def update_payment_method(body: Dict) -> Dict:
    """支払い方法更新処理"""
    try:
        customer_id = body['customerId']
        token = body['token']

        # 既存の支払い方法を削除
        payment_methods = stripe.PaymentMethod.list(
            customer=customer_id,
            type='card'
        )
        for pm in payment_methods.data:
            stripe.PaymentMethod.detach(pm.id)

        # 新しい支払い方法を追加
        payment_method = stripe.PaymentMethod.create(
            type='card',
            card={'token': token}
        )
        stripe.PaymentMethod.attach(
            payment_method.id,
            customer=customer_id
        )

        return {
            'message': '支払い方法が正常に更新されました',
            'paymentMethod': {
                'id': payment_method.id,
                'brand': payment_method.card.brand,
                'last4': payment_method.card.last4,
                'expMonth': payment_method.card.exp_month,
                'expYear': payment_method.card.exp_year
            }
        }
    except Exception as e:
        return {
            'error': str(e)
        }

def get_invoices(body: Dict) -> Dict:
    """請求履歴取得処理"""
    try:
        customer_id = body.get('customerId')
        if not customer_id:
            return {'data': {'invoices': []}}

        invoices = stripe.Invoice.list(
            customer=customer_id,
            limit=6  # 直近6ヶ月分
        )

        return {
            'data': {
                'invoices': [{
                    'id': invoice.id,
                    'date': invoice.created * 1000,  # 秒をミリ秒に変換
                    'amount': invoice.amount_paid,
                    'status': invoice.status,
                    'description': invoice.lines.data[0].description if invoice.lines.data else '',
                    'url': invoice.hosted_invoice_url
                } for invoice in invoices.data]
            }
        }
    except Exception as e:
        return {'data': {'invoices': []}, 'error': str(e)}

def get_subscription_info(customer_id: str) -> Dict:
    """顧客IDからサブスクリプション情報を取得"""
    try:
        subscriptions = stripe.Subscription.list(
            customer=customer_id,
            limit=1,
            status='active',
            expand=['data.items.data.price']  # priceの詳細情報を展開
        )

        if not subscriptions.data:
            return {
                'planId': 'free',
                'accountCount': 0,
                'subscriptionId': None,
                'stripeCustomerId': customer_id
            }

        subscription = subscriptions.data[0]
        account_count = int(subscription.metadata.get('account_count', 0))
        
        # プランIDをメタデータから直接取得
        plan_id = subscription.metadata.get('plan_id', 'free')
        
        # 価格IDをlookupテーブルから逆引き
        price_id = None
        for config_price_id, config_plan in PaymentConfig.PRICE_TO_PLAN_MAP.items():
            if config_plan == plan_id:
                price_id = config_price_id
                break
        
        return {
            'planId': plan_id,
            'priceId': price_id,
            'accountCount': account_count,
            'subscriptionId': subscription.id,
            'stripeCustomerId': customer_id
        }

    except stripe.error.StripeError as e:
        raise PaymentError(f'サブスクリプション情報の取得に失敗しました: {str(e)}')

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """メインハンドラー関数"""
    try:
        path = event.get('path', '')
        method = event.get('httpMethod', '')
        body = json.loads(event.get('body', '{}'))

        handlers = {
            '/payment/create-subscription': create_subscription,
            '/payment/update-subscription': update_subscription,
            '/payment/change-plan': change_subscription_plan,
            '/payment/payment-methods': get_payment_methods,
            '/payment/update-payment-method': update_payment_method,
            '/payment/invoices': get_invoices,
            '/payment/subscription-info': lambda body: {'data': get_subscription_info(body['customerId'])}
        }

        if (method != 'POST' or path not in handlers):
            return create_response(404, {'error': '指定されたエンドポイントは存在しません'})

        result = handlers[path](body)
        return create_response(200, result)

    except PaymentError as e:
        # PaymentErrorは400エラーとして返す
        return create_response(400, {'error': str(e)})
    except stripe.error.StripeError as e:
        # Stripeのエラーも400エラーとして返す
        return create_response(400, {'error': str(e)})
    except Exception as e:
        import traceback
        error_message = {
            'error': 'システムエラーが発生しました',  # ユーザー向けの一般的なエラーメッセージ
            'detail': str(e),  # 詳細なエラー情報
            'traceback': traceback.format_exc()  # デバッグ用のスタックトレース
        }
        print('Error:', error_message)  # ログ出力
        return create_response(500, {'error': 'システムエラーが発生しました'})  # クライアントへの応答