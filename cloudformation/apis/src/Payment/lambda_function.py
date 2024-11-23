import json
import stripe
import os
import time
import traceback
import uuid
import logging
import datetime
from typing import Dict, Any
from common.utils import create_response

# ロガーの設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)

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

    # 環境設定
    STAGE_TO_ENV_MAP = {
        'dev': 'development',
        'prod': 'production'
    }
    ENVIRONMENT = STAGE_TO_ENV_MAP.get(os.environ.get('STAGE', 'dev'), 'development')

    # 冪等性設定
    IDEMPOTENCY_KEY_TTL = 24 * 3600  # 24時間
    
    # カードエラーメッセージ（国際化対応）
    CARD_ERROR_MESSAGES = {
        'card_declined': '決済が拒否されました。',
        'expired_card': 'カードの有効期限が切れています。',
        'incorrect_cvc': 'セキュリティコードが正しくありません。',
        'processing_error': '決済処理中にエラーが発生しました。',
        'incorrect_number': 'カード番号が正しくありません。',
        'invalid_expiry_month': '有効期限の月が無効です。',
        'invalid_expiry_year': '有効期限の年が無効です。'
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

def log_error(error: Exception, additional_info: dict = None) -> None:
    """エラーログの記録"""
    error_info = {
        'error_type': type(error).__name__,
        'error_message': str(error),
        'timestamp': time.time(),
        'environment': PaymentConfig.ENVIRONMENT
    }
    if additional_info:
        error_info.update(additional_info)
    
    logger.error(f"Payment Error: {json.dumps(error_info)}")
    if isinstance(error, stripe.error.StripeError):
        logger.error(f"Stripe Error Details: {error.json_body}")

def get_card_error_message(error: stripe.error.CardError) -> str:
    """カードエラーメッセージの取得"""
    error_code = error.code
    decline_code = error.decline_code
    return PaymentConfig.CARD_ERROR_MESSAGES.get(
        decline_code or error_code,
        'カード決済に失敗しました。'
    )

def create_error_response(error: Exception) -> Dict:
    """エラーレスポンスの生成"""
    if isinstance(error, stripe.error.StripeError):
        return create_response(400, {'error': str(error)})
    if isinstance(error, PaymentError):
        return create_response(400, {'error': str(error)})
    return create_response(500, {'error': 'Internal server error'})

def get_or_create_customer(email: str, token: str, client_ip: str) -> stripe.Customer:
    """顧客の取得または作成"""
    customers = stripe.Customer.list(email=email, limit=1)
    if customers.data:
        return customers.data[0]
    return stripe.Customer.create(
        email=email,
        source=token,
        preferred_locales=['ja'],  # 言語を日本語に設定
        tax={
            'ip_address': client_ip  # クライアントのIPアドレスを使用
        }
    )

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

def create_subscription(body: Dict, client_ip: str) -> Dict:
    """サブスクリプション作成処理"""
    try:
        # 冪等性キーの取得
        idempotency_key = body.get('idempotencyKey', str(uuid.uuid4()))
        
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
            customer = get_or_create_customer(email, token, client_ip)
            # Cognitoの更新は不要（フロントエンドで行う）

        # Stripe APIコールの共通パラメータ
        stripe_params = {
            'idempotency_key': idempotency_key,
            'stripe_version': '2023-10-16'
        }

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
                        'plan_id': 'business',  # planIdをメタデータに保存
                        'environment': PaymentConfig.ENVIRONMENT,
                        'created_at': str(int(time.time()))
                    },
                    payment_behavior='error_if_incomplete',
                    **stripe_params
                )
            else:  # プロプラン
                subscription = stripe.Subscription.create(
                    customer=customer.id,
                    items=[{'price': price_id}],
                    metadata={
                        'plan_id': 'pro',  # planIdをメタデータに保存
                        'environment': PaymentConfig.ENVIRONMENT,
                        'created_at': str(int(time.time()))
                    },
                    payment_behavior='error_if_incomplete',
                    **stripe_params
                )
            
            logger.info(f"Subscription created successfully: {subscription.id}")
            return create_subscription_response(subscription, price_id, account_count)
            
        except stripe.error.CardError as e:
            error_msg = get_card_error_message(e)
            log_error(e, {'customer_id': customer.id, 'price_id': price_id})
            raise PaymentError(error_msg)
        except stripe.error.StripeError as e:
            log_error(e, {'customer_id': customer.id, 'price_id': price_id})
            raise
            
    except Exception as e:
        log_error(e, {'body': body})
        raise

def update_subscription(body: Dict) -> Dict:
    """サブスクリプション更新処理"""
    new_account_count = int(body.get('newAccountCount', 0))
    subscription_id = body['subscriptionId']

    subscription = stripe.Subscription.retrieve(subscription_id)
    subscription_item = subscription['items']['data'][0]

    # 新しい金額を計算
    new_price = calculate_business_price(new_account_count)

    # アカウント数のみの変更なのでプロレーションなし
    stripe.SubscriptionItem.modify(
        subscription_item.id,
        price_data={
            'currency': PaymentConfig.CURRENCY,
            'product': subscription_item.price.product,
            'unit_amount': new_price,
            'recurring': {'interval': PaymentConfig.BILLING_INTERVAL}
        },
        proration_behavior='none'  # プロレーションを無効化
    )

    # メタデータの更新のみ
    stripe.Subscription.modify(
        subscription_id,
        metadata={'account_count': str(new_account_count)}
    )

    return create_subscription_response(
        stripe.Subscription.retrieve(subscription_id),
        PaymentConfig.PRICE_ID_BUSINESS,
        new_account_count,
        message=ResponseMessages.ACCOUNT_COUNT_UPDATED
    )

def handle_paid_plan_change(subscription: stripe.Subscription, new_price_id: str, new_account_count: int) -> Dict:
    """有料プラン間の変更処理"""
    try:
        subscription_item = subscription['items']['data'][0]
        current_product = subscription_item.price.product
        
        # 同じビジネスプラン内でのアカウント数変更の場合
        if (new_price_id == PaymentConfig.PRICE_ID_BUSINESS and 
            current_product == PaymentConfig.PRODUCT_ID_BUSINESS):
            
            # 即時のアカウント数と金額更新
            new_price = calculate_business_price(new_account_count)
            
            # 現在のインボイス期間を取得
            current_period_start = subscription.current_period_start
            current_period_end = subscription.current_period_end
            
            # プロレーション金額を計算（日割り）
            proration_date = int(time.time())
            preview_invoice = stripe.Invoice.upcoming(
                customer=subscription.customer,
                subscription=subscription.id,
                subscription_items=[{
                    'id': subscription_item.id,
                    'price_data': {
                        'currency': PaymentConfig.CURRENCY,
                        'product': PaymentConfig.PRODUCT_ID_BUSINESS,
                        'unit_amount': new_price,
                        'recurring': {'interval': PaymentConfig.BILLING_INTERVAL}
                    }
                }],
                subscription_proration_date=proration_date
            )
            
            # インボイスプレビューをログ出力
            print(f"Debug - Preview invoice: {json.dumps(preview_invoice, indent=2)}")
            
            # サブスクリプションアイテムの更新（プロレーションあり）
            stripe.SubscriptionItem.modify(
                subscription_item.id,
                price_data={
                    'currency': PaymentConfig.CURRENCY,
                    'product': PaymentConfig.PRODUCT_ID_BUSINESS,
                    'unit_amount': new_price,
                    'recurring': {'interval': PaymentConfig.BILLING_INTERVAL}
                },
                proration_behavior='always_invoice'  # 即時請求に変更
            )
            
        else:
            # 異なるプラン間の変更の場合
            update_params = {
                'proration_behavior': 'always_invoice',  # 即時請求に変更
                'collection_method': 'charge_automatically'
            }

            if new_price_id == PaymentConfig.PRICE_ID_BUSINESS:
                update_params['price_data'] = {
                    'currency': PaymentConfig.CURRENCY,
                    'product': PaymentConfig.PRODUCT_ID_BUSINESS,
                    'unit_amount': calculate_business_price(new_account_count),
                    'recurring': {'interval': PaymentConfig.BILLING_INTERVAL}
                }
            else:
                update_params['price'] = new_price_id

            # サブスクリプションアイテムの更新
            stripe.SubscriptionItem.modify(subscription_item.id, **update_params)

        # メタデータの更新
        updated_subscription = stripe.Subscription.modify(
            subscription.id,
            metadata={
                'account_count': str(new_account_count),
                'last_change_at': str(int(time.time())),
                'plan_id': PaymentConfig.PRICE_TO_PLAN_MAP.get(new_price_id, 'free')
            },
            cancel_at_period_end=False
        )
        
        return create_subscription_response(
            updated_subscription,
            new_price_id,
            new_account_count
        )
        
    except stripe.error.StripeError as e:
        print(f"Error in handle_paid_plan_change: {str(e)}")
        raise PaymentError(f'プラン変更に失敗しました: {str(e)}')

def change_subscription_plan(body: Dict) -> Dict:
    """プラン変更処理"""
    try:
        subscription_id = body['subscriptionId']
        new_price_id = body['priceId']
        new_account_count = int(body.get('accountCount', 0))
        customer_id = body.get('customerId')

        # フリープランからの変更
        if subscription_id == PaymentConfig.PRICE_ID_FREE:
            return create_subscription({
                **body,
                'customerId': customer_id
            }, body.get('clientIp', 'auto'))

        subscription = stripe.Subscription.retrieve(subscription_id)
        
        # フリープランへの変更
        if new_price_id == PaymentConfig.PRICE_ID_FREE:
            return handle_free_plan_change(subscription, {
                **body,
                'customerId': subscription.customer
            })

        # 通常のプラン変更
        check_plan_change_cooldown(subscription)
        return handle_paid_plan_change(subscription, new_price_id, new_account_count)

    except stripe.error.InvalidRequestError as e:
        if new_price_id == PaymentConfig.PRICE_ID_FREE:
            return create_free_plan_response(customer_id or body.get('customerId'))
        raise e

def create_free_plan_response(customer_id: str = None) -> Dict:
    """フリープランレスポンスの生成"""
    return {
        'message': 'フリープランが選択されました',
        'subscription': {
            'id': 'free',
            'planId': 'free',
            'priceId': PaymentConfig.PRICE_ID_FREE,  # priceをpriceIdに変更
            'accountCount': 0,
            'status': 'active',
            'stripeCustomerId': customer_id,
            'subscriptionId': None
        }
    }

def calculate_days_from_timestamp(start_time: int, end_time: int) -> int:
    """2つのタイムスタンプ間の日数を計算（1日未満は切り上げ）"""
    seconds_diff = end_time - start_time
    days = (seconds_diff + PaymentConfig.SECONDS_PER_DAY - 1) // PaymentConfig.SECONDS_PER_DAY
    return max(1, int(days))  # 最低1日として扱う

def handle_free_plan_change(subscription: stripe.Subscription, body: Dict) -> Dict:
    """フリープランへの変更処理"""
    customer_id = subscription.customer
    
    try:
        current_time = int(time.time())
        period_end = subscription.current_period_end
        period_start = subscription.current_period_start
        
        # 利用日数の計算（1日未満は1日として計算）
        used_days = calculate_days_from_timestamp(period_start, current_time)
        total_days = calculate_days_from_timestamp(period_start, period_end)
        
        # まず請求書を作成して日割り金額を計算
        upcoming_invoice = stripe.Invoice.upcoming(
            customer=customer_id,
            subscription=subscription.id
        )
        
        # サブスクリプションを即時キャンセル
        canceled_subscription = stripe.Subscription.delete(
            subscription.id,
            prorate=True,  # 日割り計算を有効化
            invoice_now=True  # 即時請求
        )
        
        print(f"Debug - Subscription canceled with proration: used_days={used_days}, total_days={total_days}")
        print(f"Debug - Upcoming invoice: {json.dumps(upcoming_invoice, indent=2)}")
        print(f"Debug - Cancel details: {json.dumps(canceled_subscription, indent=2)}")
        
        return {
            'message': f'プランを解約し、フリープランに変更しました（利用日数: {used_days}日）',
            'subscription': {
                'id': 'free',
                'planId': 'free',
                'priceId': PaymentConfig.PRICE_ID_FREE,
                'status': 'active',
                'stripeCustomerId': customer_id,
                'accountCount': 0,
                'subscriptionId': None,
                'usedDays': used_days,
                'totalDays': total_days
            }
        }
        
    except stripe.error.StripeError as e:
        print(f"Error canceling subscription: {str(e)}")
        raise PaymentError(f'プラン変更に失敗しました: {str(e)}')

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
    """支払い方��取得処理"""
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

def format_date_for_description(timestamp):
    """説明文用の日付フォーマット"""
    date = datetime.datetime.fromtimestamp(timestamp)
    return date.strftime('%Y/%m/%d')

def convert_description_date(description: str, period_start: int) -> str:
    """説明文内の日付と料金表記を変換"""
    if not description:
        return description

    # より後の日付の変換
    if 'より後の' in description:
        parts = description.split('より後の')
        if len(parts) == 2:
            date_str = format_date_for_description(period_start)
            description = f'{date_str}より後の{parts[1]}'
    
    # プラン名と料金表記の変換
    if ' × ' in description and '/ month)' in description:
        # 1 × ビジネスプラン (at ¥4,500 / month) → ビジネスプラン (¥4,500 / 月)
        parts = description.split(' × ')
        if len(parts) == 2:
            plan_part = parts[1]
            if '(at ' in plan_part and ' / month)' in plan_part:
                plan_name = plan_part.split(' (at ')[0].strip()
                price = plan_part.split(' (at ')[1].replace(' / month)', ' / 月')
                description = f'{plan_name} ({price})'
    
    return description

def get_invoices(body: Dict) -> Dict:
    try:
        customer_id = body.get('customerId')
        if not customer_id:
            return {'data': {'invoices': []}}

        formatted_transactions = []

        # すべての請求書を取得（最新の状態を含める）
        invoices = stripe.Invoice.list(
            customer=customer_id,
            limit=24,  # 取得上限を増やす
            expand=['data.charge', 'data.lines.data']
        )

        # 保留中のインボイスを取得（プロレーション含む）
        try:
            upcoming = stripe.Invoice.upcoming(
                customer=customer_id,
                expand=['lines.data']
            )
            print(f"Debug - Upcoming invoice: {json.dumps(upcoming, indent=2)}")
            
            # 保留中のインボイスアイテムを処理
            for line in upcoming.lines.data:
                description = convert_description_date(line.description, line.period.start)
                
                formatted_transactions.append({
                    'id': f"upcoming_{line.id}",
                    'date': line.period.start,
                    'amount': line.amount,
                    'status': 'upcoming',
                    'type': 'proration' if line.type == 'invoiceitem' else 'charge',
                    'description': description or 'プラン変更に伴う調整',
                    'url': None,
                    'upcoming': True
                })
        except stripe.error.InvalidRequestError as e:
            print(f"Debug - No upcoming invoice: {str(e)}")
            pass

        # 既存のインボイス処理
        for invoice in invoices.data:
            print(f"Debug - Processing invoice: {invoice.id}")
            
            # 通常の請求とプロレーション処理
            for line in invoice.lines.data:
                description = convert_description_date(line.description, line.period.start)
                
                formatted_transactions.append({
                    'id': f"{invoice.id}_{line.id}",
                    'date': line.period.start,
                    'amount': line.amount,
                    'status': invoice.status,
                    'type': 'proration' if line.type == 'invoiceitem' else 'charge',
                    'description': description or '定期購読料金',
                    'url': invoice.hosted_invoice_url
                })

            # 返金処理
            if invoice.charge:
                refunds = stripe.Refund.list(charge=invoice.charge)
                for refund in refunds.data:
                    formatted_transactions.append({
                        'id': refund.id,
                        'date': refund.created,
                        'amount': -refund.amount,
                        'status': refund.status,
                        'type': 'refund',
                        'description': '返金',
                        'url': None
                    })

        # 日付でソート（新しい順）
        formatted_transactions.sort(key=lambda x: x['date'], reverse=True)
        
        print(f"Debug - Final transactions: {json.dumps(formatted_transactions, indent=2)}")

        return {'data': {'invoices': formatted_transactions}}
        
    except Exception as e:
        print(f"Error fetching invoices: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return {'data': {'invoices': []}, 'error': str(e)}

def get_subscription_info(customer_id: str) -> Dict:
    """顧客IDからサブスクリプション情報を取得"""
    try:
        subscriptions = stripe.Subscription.list(
            customer=customer_id,
            limit=1,
            status='active',
            expand=['data.items.data.price']
        )

        if not subscriptions.data:
            return {
                'planId': 'free',
                'priceId': PaymentConfig.PRICE_ID_FREE,  # 明示的に設定
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
    request_id = context.aws_request_id
    logger.info(f"Processing request: {request_id}")
    
    try:
        path = event.get('path', '')
        method = event.get('httpMethod', '')
        body = json.loads(event.get('body', '{}'))
        
        # クライアントIPアドレスの取得
        client_ip = event.get('requestContext', {}).get('identity', {}).get('sourceIp', 'auto')

        handlers = {
            '/payment/create-subscription': lambda body: create_subscription(body, client_ip),
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
        log_error(e, {'request_id': request_id, 'path': event.get('path')})
        return create_response(400, {'error': str(e)})
    except stripe.error.StripeError as e:
        log_error(e, {'request_id': request_id, 'path': event.get('path')})
        return create_response(400, {'error': str(e)})
    except Exception as e:
        log_error(e, {
            'request_id': request_id,
            'path': event.get('path'),
            'traceback': traceback.format_exc()
        })
        return create_response(500, {'error': 'システムエラーが発生しました'})