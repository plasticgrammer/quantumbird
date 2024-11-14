import json
import stripe
import os
from typing import Dict, Any
from common.utils import create_response

# Stripe APIキーの設定
stripe.api_key = os.environ['STRIPE_SECRET_KEY']

# プラン関連の定数
PRICE_ID_FREE = 'price_free'
PRICE_ID_PRO = 'price_1QJSigJlLYAT4bpznFUNs5eg'
PRICE_ID_BUSINESS = 'price_1QJSmjJlLYAT4bpzzPjAgcJj'
PRODUCT_ID_BUSINESS = 'prod_RBqT2Wa1VvXK56'

# 料金関連の定数
BUSINESS_BASE_PRICE = 2000
BUSINESS_PER_ACCOUNT_PRICE = 500

# 設定値の定数
VALID_PRICE_IDS = [PRICE_ID_FREE, PRICE_ID_PRO, PRICE_ID_BUSINESS]
CURRENCY = 'jpy'
BILLING_INTERVAL = 'month'

def create_subscription(body: Dict) -> Dict:
    """サブスクリプション作成処理"""
    email = body['email']
    token = body['token']
    price_id = body['priceId']
    account_count = int(body.get('accountCount', 0))  # 文字列を整数に変換

    # プランIDの検証
    valid_price_ids = VALID_PRICE_IDS
    if price_id not in valid_price_ids:
        raise ValueError('無効なプランIDです')

    # 顧客の作成または取得
    customers = stripe.Customer.list(email=email, limit=1)
    if customers.data:
        customer = customers.data[0]
    else:
        customer = stripe.Customer.create(
            email=email,
            source=token
        )

    # プランに応じた価格設定とサブスクリプション作成
    if price_id == PRICE_ID_BUSINESS:  # ビジネスプラン
        total_price = BUSINESS_BASE_PRICE + (account_count * BUSINESS_PER_ACCOUNT_PRICE)
        subscription = stripe.Subscription.create(
            customer=customer.id,
            items=[{
                'price_data': {
                    'currency': CURRENCY,
                    'product': PRODUCT_ID_BUSINESS,  # 商品IDを直接指定
                    'unit_amount': total_price,
                    'recurring': {'interval': BILLING_INTERVAL}
                }
            }],
            metadata={'account_count': str(account_count)}
        )
    elif price_id != PRICE_ID_FREE:  # プロプラン
        subscription = stripe.Subscription.create(
            customer=customer.id,
            items=[{'price': price_id}]
        )
    else:  # フリープラン
        return {
            'message': 'フリープランが選択されました',
            'subscription': {
                'id': 'free',
                'price': price_id,
                'accountCount': 0,
                'status': 'active'
            }
        }

    return {
        'message': 'サブスクリプションが正常に作成されました',
        'subscription': {
            'id': subscription.id,
            'price': price_id,
            'accountCount': account_count,
            'status': subscription.status
        }
    }

def update_subscription(body: Dict) -> Dict:
    """サブスクリプション更新処理"""
    new_account_count = int(body.get('newAccountCount', 0))  # 文字列を整数に変換
    subscription_id = body['subscriptionId']

    # サブスクリプションの取得と更新
    subscription = stripe.Subscription.retrieve(subscription_id)
    subscription_item = subscription['items']['data'][0]

    # 新しい金額の計算と更新
    base_price = BUSINESS_BASE_PRICE
    per_account_price = BUSINESS_PER_ACCOUNT_PRICE
    new_price = base_price + (new_account_count * per_account_price)

    # サブスクリプションの更新
    stripe.SubscriptionItem.modify(
        subscription_item.id,
        price_data={
            'currency': CURRENCY,
            'product': subscription_item.price.product,
            'unit_amount': new_price,
            'recurring': {'interval': BILLING_INTERVAL}
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

def change_subscription_plan(body: Dict) -> Dict:
    """プラン変更処理"""
    subscription_id = body['subscriptionId']
    new_price_id = body['priceId']
    new_account_count = int(body.get('accountCount', 0))

    # フリープランからの変更の場合は新規サブスクリプション作成
    if subscription_id == 'free':
        return create_subscription({
            'email': body['email'],
            'token': body['token'],
            'priceId': new_price_id,
            'accountCount': new_account_count
        })

    # 既存のサブスクリプションを取得
    try:
        subscription = stripe.Subscription.retrieve(subscription_id)
    except stripe.error.StripeError as e:
        if new_price_id == PRICE_ID_FREE:
            # サブスクリプションが見つからない場合でも、フリープランへの変更は許可
            return {
                'message': 'フリープランに変更されました',
                'subscription': {
                    'id': 'free',
                    'price': new_price_id,
                    'accountCount': 0,
                    'status': 'canceled'
                }
            }
        raise e

    # フリープランへの変更の場合はサブスクリプションを次回支払い日で解約
    if new_price_id == PRICE_ID_FREE:
        try:
            canceled_subscription = stripe.Subscription.delete(
                subscription_id,
                at_period_end=True  # 次回支払い日でキャンセル
            )
            return {
                'message': '次回支払い日でフリープランに変更されます',
                'subscription': {
                    'id': subscription_id,  # フリープランに変更されるまでは既存のサブスクリプションIDを保持
                    'price': new_price_id,
                    'accountCount': 0,
                    'status': canceled_subscription.status,
                    'cancelAt': canceled_subscription.cancel_at  # キャンセル予定日
                }
            }
        except stripe.error.StripeError as e:
            # サブスクリプションの解約に失敗しても、フリープランへの変更は許可
            return {
                'message': 'フリープランに変更されました',
                'subscription': {
                    'id': 'free',
                    'price': new_price_id,
                    'accountCount': 0,
                    'status': 'canceled'
                }
            }

    # 他のプランへの変更処理
    subscription = stripe.Subscription.retrieve(subscription_id)
    customer_id = subscription.customer
    current_price_id = subscription['items']['data'][0].price.id
    
    # 有���プラン間の変更（ビジネスプランへの変更またはビジネスプランからの変更）
    if (new_price_id == PRICE_ID_BUSINESS or 
        current_price_id == PRICE_ID_BUSINESS):
        # 既存のサブスクリプションを解約
        stripe.Subscription.delete(subscription_id)
        
        # 新しいサブスクリプション設定を準備
        if new_price_id == PRICE_ID_BUSINESS:  # ビジネスプランへの変更
            total_price = BUSINESS_BASE_PRICE + (new_account_count * BUSINESS_PER_ACCOUNT_PRICE)
            subscription_items = [{
                'price_data': {
                    'currency': CURRENCY,
                    'product': PRODUCT_ID_BUSINESS,
                    'unit_amount': total_price,
                    'recurring': {'interval': BILLING_INTERVAL}
                }
            }]
            metadata = {'account_count': str(new_account_count)}
        else:  # ビジネスプランからの変更
            subscription_items = [{'price': new_price_id}]
            metadata = {}
        
        # 新しいサブスクリプションを作成
        subscription_response = stripe.Subscription.create(
            customer=customer_id,
            items=subscription_items,
            metadata=metadata
        )
    
    else:  # その他のプラン間の変更
        # プランの変更
        stripe.Subscription.modify(
            subscription_id,
            items=[{
                'id': subscription['items']['data'][0].id,
                'price': new_price_id
            }],
            proration_behavior='always_invoice'
        )
        subscription_response = stripe.Subscription.retrieve(subscription_id)

    return {
        'message': 'プランが正常に変更されました',
        'subscription': {
            'id': subscription_response.id,
            'price': new_price_id,
            'accountCount': new_account_count,
            'status': subscription_response.status
        }
    }

def get_payment_methods(body: Dict) -> Dict:
    """支払い方法取得処理"""
    try:
        email = body.get('email')
        if not email:
            return {
                'data': {
                    'paymentMethods': []
                }
            }
        
        # メールアドレスから顧客を検索
        customers = stripe.Customer.list(email=email, limit=1)
        if not customers.data:
            return {
                'data': {
                    'paymentMethods': []
                }
            }
        
        customer = customers.data[0]
        
        # 顧客の支払い方法を取得
        payment_methods = stripe.PaymentMethod.list(
            customer=customer.id,
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
        return {
            'data': {
                'paymentMethods': []
            },
            'error': str(e)
        }

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

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """メインハンドラー関数"""
    try:
        # パスの取得とルーティング
        path = event.get('path', '')
        method = event.get('httpMethod', '')
        body = json.loads(event.get('body', '{}'))

        # パスベースでの処理分岐
        if path == '/payment/create-subscription' and method == 'POST':
            result = create_subscription(body)
        elif path == '/payment/update-subscription' and method == 'POST':
            result = update_subscription(body)
        elif path == '/payment/change-plan' and method == 'POST':
            result = change_subscription_plan(body)
        elif path == '/payment/payment-methods' and method == 'POST':
            result = get_payment_methods(body)
        elif path == '/payment/update-payment-method' and method == 'POST':
            result = update_payment_method(body)
        else:
            return create_response(404, {'error': '指定されたエンドポイントは存在しません'})

        return create_response(200, result)

    except stripe.error.StripeError as e:
        return create_response(400, {'error': str(e)})
    except Exception as e:
        return create_response(500, {'error': str(e)})