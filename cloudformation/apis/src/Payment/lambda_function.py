import json
import stripe
import os
from typing import Dict, Any
from common.utils import create_response

# Stripe APIキーの設定
stripe.api_key = os.environ['STRIPE_SECRET_KEY']

def create_subscription(body: Dict) -> Dict:
    """サブスクリプション作成処理"""
    email = body['email']
    token = body['token']
    price_id = body['priceId']
    account_count = int(body.get('accountCount', 0))  # 文字列を整数に変換

    # プランIDの検証
    valid_price_ids = ['price_free', 'price_1QJSigJlLYAT4bpznFUNs5eg', 'price_1QJSmjJlLYAT4bpzzPjAgcJj']
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
    if price_id == 'price_1QJSmjJlLYAT4bpzzPjAgcJj':  # ビジネスプラン
        base_price = 2000
        per_account_price = 300
        total_price = base_price + (account_count * per_account_price)
        subscription = stripe.Subscription.create(
            customer=customer.id,
            items=[{
                'price_data': {
                    'currency': 'jpy',
                    'product': 'prod_RBqT2Wa1VvXK56',  # 商品IDを直接指定
                    'unit_amount': total_price,
                    'recurring': {'interval': 'month'}
                }
            }],
            metadata={'account_count': str(account_count)}
        )
    elif price_id != 'price_free':  # プロプラン
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
                'accountCount': 0
            }
        }

    return {
        'message': 'サブスクリプションが正常に作成されました',
        'subscription': {
            'id': subscription.id,
            'price': price_id,
            'accountCount': account_count
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
    base_price = 2000
    per_account_price = 300
    new_price = base_price + (new_account_count * per_account_price)

    # サブスクリプションの更新
    stripe.SubscriptionItem.modify(
        subscription_item.id,
        price_data={
            'currency': 'jpy',
            'product': subscription_item.price.product,
            'unit_amount': new_price,
            'recurring': {'interval': 'month'}
        }
    )

    # メタデータの更新
    stripe.Subscription.modify(
        subscription_id,
        metadata={'account_count': str(new_account_count)}
    )

    return {
        'message': 'アカウント数が正常に更新されました',
        'subscription': {
            'id': subscription_id,
            'accountCount': new_account_count
        }
    }

def change_subscription_plan(body: Dict) -> Dict:
    """プラン変更処理"""
    subscription_id = body['subscriptionId']
    new_price_id = body['priceId']
    new_account_count = int(body.get('accountCount', 0))  # 文字列を整数に変換

    # サブスクリプションの取得
    subscription = stripe.Subscription.retrieve(subscription_id)

    if new_price_id == 'price_1QJSmjJlLYAT4bpzzPjAgcJj':  # ビジネスプラン
        base_price = 2000
        per_account_price = 300
        total_price = base_price + (new_account_count * per_account_price)
        
        # 既存のサブスクリプションアイテムを更新
        stripe.SubscriptionItem.modify(
            subscription['items']['data'][0].id,
            price_data={
                'currency': 'jpy',
                'product': 'prod_RBqT2Wa1VvXK56',
                'unit_amount': total_price,
                'recurring': {'interval': 'month'}
            }
        )
        # メタデータの更新
        stripe.Subscription.modify(
            subscription_id,
            metadata={'account_count': str(new_account_count)}
        )
    else:  # その他のプラン
        # プランの変更
        stripe.Subscription.modify(
            subscription_id,
            items=[{
                'id': subscription['items']['data'][0].id,
                'price': new_price_id
            }],
            proration_behavior='always_invoice'
        )

    return {
        'message': 'プランが正常に変更されました',
        'subscription': {
            'id': subscription_id,
            'price': new_price_id,
            'accountCount': new_account_count
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