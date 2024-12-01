import stripe
import logging
import json
import time
import datetime
from typing import Dict, Any, Optional, List
from payment_config import PaymentConfig

logger = logging.getLogger()

class PaymentError(Exception):
    """支払い処理に関するカスタムエラー"""
    pass

class StripeService:
    def __init__(self):
        stripe.api_key = PaymentConfig.API_KEY
        self.logger = logger

    def _setup_logging(self):
        """ロギング設定"""
        self.logger.setLevel(logging.INFO)

    def _get_card_error_message(self, error: stripe.error.CardError) -> str:
        """カードエラーメッセージの取得"""
        decline_code = error.error.decline_code
        error_code = error.code
        return PaymentConfig.CARD_ERROR_MESSAGES.get(
            decline_code or error_code,
            'カード決済に失敗しました。'
        )

    def _handle_error(self, operation: str, error: Exception, **context) -> None:
        """エラーハンドリングの共通処理"""
        self._log_error(error, {
            'operation': operation,
            **context
        })
        
        if isinstance(error, ValueError):
            raise PaymentError(str(error))
        elif isinstance(error, stripe.error.CardError):
            raise PaymentError(self._get_card_error_message(error))
        elif isinstance(error, stripe.error.StripeError):
            raise PaymentError(f'{operation}に失敗しました: {str(error)}')
        else:
            raise PaymentError(PaymentConfig.RESPONSE_MESSAGES['system_error'])

    def _log_error(self, error: Exception, additional_info: dict = None) -> None:
        """エラーログの記録"""
        error_info = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'timestamp': time.time(),
            'environment': PaymentConfig.ENVIRONMENT
        }
        if additional_info:
            error_info.update(additional_info)
        
        self.logger.error(f"Payment Error: {json.dumps(error_info)}")

    def _get_customer(self, email: str = None, customer_id: str = None) -> Optional[stripe.Customer]:
        """顧客情報の取得（emailまたはcustomer_idで検索）"""
        try:
            if customer_id:
                return stripe.Customer.retrieve(customer_id)
            if email:
                customers = stripe.Customer.list(email=email, limit=1)
                return customers.data[0] if customers.data else None
            return None
        except stripe.error.StripeError as e:
            self._handle_error('顧客情報の取得', e, email=email, customer_id=customer_id)

    # 顧客管理関連
    def get_or_create_customer(self, email: str, token: str, client_ip: str) -> stripe.Customer:
        """顧客の取得または作成"""
        customers = stripe.Customer.list(email=email, limit=1)
        if customers.data:
            return customers.data[0]
        return stripe.Customer.create(
            email=email,
            source=token,
            preferred_locales=['ja'],
            tax={'ip_address': client_ip}
        )

    # サブスクリプション関連
    def create_subscription(self, customer_id: str, price_id: str, metadata: Dict[str, str],
                          account_count: int = 0, **kwargs) -> stripe.Subscription:
        """サブスクリプションの作成"""
        if price_id == PaymentConfig.PRICE_ID_BUSINESS:
            total_price = self.calculate_business_price(account_count)
            subscription_items = [{
                'price_data': {
                    'currency': PaymentConfig.CURRENCY,
                    'product': PaymentConfig.PRODUCT_ID_BUSINESS,
                    'unit_amount': total_price,
                    'recurring': {'interval': PaymentConfig.BILLING_INTERVAL}
                }
            }]
        else:
            subscription_items = [{'price': price_id}]

        return stripe.Subscription.create(
            customer=customer_id,
            items=subscription_items,
            metadata=metadata,
            payment_behavior='error_if_incomplete',
            **kwargs
        )

    def modify_subscription(self, subscription_id: str, metadata: Dict[str, str], **kwargs) -> stripe.Subscription:
        """サブスクリプションの更新"""
        return stripe.Subscription.modify(
            subscription_id,
            metadata=metadata,
            **kwargs
        )

    def _is_business_plan_update(self, new_price_id: str, subscription_item) -> bool:
        """ビジネスプラン内での更新かどうかを判定"""
        return (new_price_id == PaymentConfig.PRICE_ID_BUSINESS and 
               subscription_item.price.product == PaymentConfig.PRODUCT_ID_BUSINESS)

    def _update_business_plan(self, subscription, subscription_item, new_account_count: int) -> Dict:
        """ビジネスプラン内での更新処理"""
        try:
            # サブスクリプションの存在確認
            try:
                current_subscription = stripe.Subscription.retrieve(subscription.id)
                if not current_subscription or current_subscription.status not in ['active', 'trialing']:
                    raise PaymentError('有効なサブスクリプションが見つかりません')
            except stripe.error.InvalidRequestError:
                raise PaymentError('無効なサブスクリプションです')

            new_price = self.calculate_business_price(new_account_count)
            
            # サブスクリプションアイテムの存在確認
            try:
                subscription_item = stripe.SubscriptionItem.retrieve(subscription_item.id)
            except stripe.error.InvalidRequestError:
                raise PaymentError('サブスクリプションアイテムが見つかりません')

            updated_subscription = self._modify_subscription_item(
                subscription_item.id,
                new_price,
                PaymentConfig.PRODUCT_ID_BUSINESS
            )
            return self._update_subscription_metadata(updated_subscription, new_account_count)
        except stripe.error.StripeError as e:
            self._log_error(e, {
                'subscription_id': subscription.id,
                'account_count': new_account_count
            })
            raise PaymentError(f'プラン更新に失敗しました: {str(e)}')

    def _change_to_different_plan(self, subscription: stripe.Subscription, 
                            subscription_item: stripe.SubscriptionItem,
                            new_price_id: str, new_account_count: int) -> Dict:
        """異なるプラン間の変更処理"""
        # 日割り計算のタイミングを即時に設定
        proration_date = int(time.time())
        
        # プロレーション処理を含む変更
        updated_subscription = stripe.Subscription.modify(
            subscription.id,
            proration_behavior='always_invoice',  # 即時に請求と返金を処理
            proration_date=proration_date,
            items=[{
                'id': subscription_item.id,
                'price': new_price_id
            }],
            metadata={
                'account_count': str(new_account_count),
                'plan_id': PaymentConfig.PRICE_TO_PLAN_MAP[new_price_id]
            }
        )
        return self.create_subscription_response(
            updated_subscription,
            new_price_id,
            new_account_count,
            message=PaymentConfig.RESPONSE_MESSAGES['plan_changed']
        )

    def create_subscription_from_request(self, body: Dict, client_ip: str) -> Dict:
        """リクエストからサブスクリプションを作成"""
        email = body['email']
        token = body.get('token')
        price_id = body['priceId']
        account_count = int(body.get('accountCount', 0))
        customer = self.get_or_create_customer(email, token, client_ip)
        metadata = self._get_subscription_metadata(price_id, account_count)
        subscription = self.create_subscription(customer.id, price_id, metadata, account_count)
        return self.create_subscription_response(subscription, price_id, account_count)

    def _get_subscription_metadata(self, price_id: str, account_count: int) -> Dict[str, str]:
        """サブスクリプションのメタデータ生成"""
        return {
            'account_count': str(account_count),
            'plan_id': PaymentConfig.PRICE_TO_PLAN_MAP[price_id],
            'environment': PaymentConfig.ENVIRONMENT,
            'created_at': str(int(time.time()))
        }

    # 支払い方法関連
    def list_payment_methods(self, customer_id: str) -> List[Dict[str, Any]]:
        """支払い方法一覧の取得"""
        try:
            if not customer_id:
                raise ValueError('顧客IDが指定されていません')

            payment_methods = stripe.PaymentMethod.list(
                customer=customer_id,
                type='card'
            )
            
            if not payment_methods.data:
                return []

            return [{
                'id': pm.id,
                'brand': pm.card.brand,
                'last4': pm.card.last4,
                'expMonth': pm.card.exp_month,
                'expYear': pm.card.exp_year
            } for pm in payment_methods.data]

        except stripe.error.InvalidRequestError as e:
            self._log_error(e, {'customer_id': customer_id})
            raise PaymentError('無効な顧客IDです')
        except stripe.error.StripeError as e:
            self._log_error(e, {'customer_id': customer_id})
            raise PaymentError('支払い方法の取得に失敗しました')
        except Exception as e:
            self._log_error(e, {'customer_id': customer_id})
            raise PaymentError('予期せぬエラーが発生しました')

    def update_payment_method(self, customer_id: str, token: str) -> Dict[str, Any]:
        """支払い方法の更新"""
        try:
            # 既存の支払い方法を削除
            for pm in self.list_payment_methods(customer_id):
                stripe.PaymentMethod.detach(pm['id'])

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
                'id': payment_method.id,
                'brand': payment_method.card.brand,
                'last4': payment_method.card.last4,
                'expMonth': payment_method.card.exp_month,
                'expYear': payment_method.card.exp_year
            }
        except stripe.error.StripeError as e:
            self._handle_error('支払い方法の更新', e, customer_id=customer_id)

    # 請求関連
    def get_upcoming_invoice(self, customer_id: str, **kwargs) -> Optional[stripe.Invoice]:
        """次回の請求書情報を取得"""
        try:
            return stripe.Invoice.upcoming(
                customer=customer_id,
                **kwargs
            )
        except stripe.error.InvalidRequestError:
            return None

    def list_invoices(self, customer_id: str, **kwargs) -> List[stripe.Invoice]:
        """請求書一覧の取得"""
        return stripe.Invoice.list(
            customer=customer_id,
            **kwargs
        ).data

    def get_formatted_invoices(self, customer_id: str) -> Dict:
        """請求書一覧の取得とフォーマット"""
        try:
            if not customer_id:
                return {'data': {'invoices': []}}

            formatted_transactions = []

            # 請求書一覧を取得
            invoices = stripe.Invoice.list(
                customer=customer_id,
                limit=24,
                expand=['data.charge', 'data.lines.data']
            )

            # 次回の請求書を取得
            try:
                upcoming = stripe.Invoice.upcoming(
                    customer=customer_id,
                    expand=['lines.data']
                )
                self.logger.debug("Upcoming invoice: %s", json.dumps(upcoming, indent=2))
                formatted_transactions.append(self._format_invoice(upcoming, is_upcoming=True))
            except stripe.error.InvalidRequestError:
                upcoming = None

            for invoice in invoices:
                formatted_transactions.append(self._format_invoice(invoice))

            return {'data': {'invoices': formatted_transactions}}
        except stripe.error.StripeError as e:
            self._handle_error('請求書の取得', e, customer_id=customer_id)

    def _format_invoice(self, invoice: stripe.Invoice, is_upcoming: bool = False) -> Dict:
        """請求書のフォーマット"""
        # upcomingインボイスの場合は仮のIDを生成
        invoice_id = getattr(invoice, 'id', 'upcoming_invoice') if not is_upcoming else 'upcoming_invoice'
        invoice_url = invoice.hosted_invoice_url if not is_upcoming else None
        description = invoice.lines.data[0].description if invoice.lines.data else '請求書'
        formatted_lines = [
            self._format_invoice_line(line, description, invoice_url, is_upcoming) 
            for line in invoice.lines.data
        ]

        return {
            'id': f"upcoming_{invoice_id}" if is_upcoming else invoice_id,
            'date': invoice.created,
            'amount': invoice.amount_due,
            'status': 'upcoming' if is_upcoming else invoice.status,
            'lines': formatted_lines,
            'url': invoice_url
        }

    def _format_date_for_description(self, timestamp: int) -> str:
        """説明文用の日付フォーマット"""
        date = datetime.datetime.fromtimestamp(timestamp)
        return date.strftime('%Y/%m/%d')

    def _convert_description_date(self, description: str, period_start: int) -> str:
        """説明文内の日付と料金表記を変換"""
        if not description:
            return description

        # 説明文のパターンに応じた変換
        if 'より後の' in description:
            # プロレーション（返金や調整）の場合
            date_str = self._format_date_for_description(period_start)
            description = description.replace('より後の', f'{date_str}以降の')
            if 'の未使用時間' in description:
                description = description.replace('の未使用時間', 'の未使用分')
            if 'の残り時間' in description:
                description = description.replace('の残り時間', 'の残り期間分')
        else:
            # 通常の請求の場合
            pattern = r'^\d{4}年\d{2}月\d{2}日分の'
            if ' × ' in description:
                description = description.split(' × ')[1]  # 数量部分を除去
            description = description.replace(' (at ¥', ' (¥')
            description = description.replace(' / month)', ' / 月)')
            description = description.replace(pattern, '')

        return description

    def _format_invoice_line(self, line: stripe.InvoiceLineItem, 
                           description: str, invoice_url: str = None, 
                           is_upcoming: bool = False) -> Dict:
        """請求明細のフォーマット"""
        line_id = getattr(line, 'id', 'line_item')

        # 説明文の変換
        formatted_description = self._convert_description_date(
            line.description or description,
            line.period.start
        )

        # プロレーション処理の場合は専用の説明文に変換
        if line.type == 'invoiceitem':
            if line.amount < 0:
                formatted_description = 'プラン変更による返金'
            else:
                formatted_description = 'プラン変更による調整'

        # statusがない場合のデフォルト値設定
        line_status = 'upcoming' if is_upcoming else getattr(line, 'status', 'paid')
        
        return {
            'id': f"upcoming_{line_id}" if is_upcoming else line_id,
            'date': line.period.start,
            'amount': line.amount,
            'status': line_status,
            'type': 'proration' if line.type == 'invoiceitem' else 'charge',
            'description': formatted_description or ('プラン変更に伴う調整' if is_upcoming else '定期購読料金'),
            'url': invoice_url,
            'upcoming': is_upcoming
        }

    def _add_refund_transactions(self, transactions: List[Dict], charge_id: str) -> None:
        """返金情報の追加"""
        refunds = stripe.Refund.list(charge=charge_id)
        for refund in refunds.data:
            transactions.append({
                'id': refund.id,
                'date': refund.created,
                'amount': -refund.amount,
                'status': refund.status,
                'type': 'refund',
                'description': '返金',
                'url': None
            })

    # ユーティリティメソッド
    @staticmethod
    def calculate_business_price(account_count: int) -> int:
        """ビジネスプランの価格計算"""
        return PaymentConfig.BUSINESS_BASE_PRICE + (account_count * PaymentConfig.BUSINESS_PER_ACCOUNT_PRICE)

    @staticmethod
    def create_subscription_response(subscription: Any, price_id: str, account_count: int, message: str = None) -> Dict:
        """サブスクリプションレスポンスの生成"""
        plan_id = PaymentConfig.PRICE_TO_PLAN_MAP.get(price_id, 'free')
        customer_id = getattr(subscription, 'customer', None)
        
        return {
            'message': message or PaymentConfig.RESPONSE_MESSAGES['subscription_created'],
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

    def get_subscription_info(self, customer_id: str) -> Dict:
        """顧客IDからサブスクリプション情報を取得"""
        try:
            subscriptions = stripe.Subscription.list(
                customer=customer_id,
                limit=1,
                status='active',
                expand=['data.items.data.price']
            )

            if not subscriptions.data:
                return self._create_free_plan_info(customer_id)

            subscription = subscriptions.data[0]
            return self._format_subscription_info(subscription, customer_id)
        except stripe.error.StripeError as e:
            self._log_error(e)
            raise PaymentError(f'サブスクリプション情報の取得に失敗しました: {str(e)}')

    def _create_free_plan_info(self, customer_id: str) -> Dict:
        """フリープラン情報の生成"""
        return {
            'planId': 'free',
            'priceId': PaymentConfig.PRICE_ID_FREE,
            'accountCount': 0,
            'subscriptionId': None,
            'stripeCustomerId': customer_id
        }

    def _format_subscription_info(self, subscription: stripe.Subscription, customer_id: str) -> Dict:
        """サブスクリプション情報のフォーマット"""
        account_count = int(subscription.metadata.get('account_count', 0))
        plan_id = subscription.metadata.get('plan_id', 'free')
        price_id = self._get_price_id_from_plan(plan_id)

        return {
            'planId': plan_id,
            'priceId': price_id,
            'accountCount': account_count,
            'subscriptionId': subscription.id,
            'stripeCustomerId': customer_id
        }

    def _get_price_id_from_plan(self, plan_id: str) -> Optional[str]:
        """プランIDから価格IDを取得"""
        for price_id, mapped_plan in PaymentConfig.PRICE_TO_PLAN_MAP.items():
            if mapped_plan == plan_id:
                return price_id
        return PaymentConfig.PRICE_ID_FREE

    def handle_plan_change(self, subscription_id: str, new_price_id: str, new_account_count: int) -> Dict:
        """プラン変更の処理"""
        try:
            subscription = stripe.Subscription.retrieve(
                subscription_id,
                expand=['items.data.price']
            )
            subscription_item = subscription['items']['data'][0]
            
            # クールダウン期間のチェック
            self._check_plan_change_cooldown(subscription)
            
            if new_price_id == PaymentConfig.PRICE_ID_FREE:
                return self._handle_free_plan_change(subscription)
            else:
                return self._handle_paid_plan_change(
                    subscription, 
                    subscription_item, 
                    new_price_id, 
                    new_account_count
                )
        except stripe.error.StripeError as e:
            self._handle_error('プラン変更', e, subscription_id=subscription_id)

    def _check_plan_change_cooldown(self, subscription: stripe.Subscription) -> None:
        """プラン変更のクールダウンチェック"""
        if subscription.metadata.get('last_change_at'):
            last_change = int(subscription.metadata.get('last_change_at'))
            if (time.time() - last_change) < PaymentConfig.PLAN_CHANGE_COOLDOWN_SECONDS:
                raise PaymentError('プラン変更は24時間に1回までです')

    def _handle_free_plan_change(self, subscription: stripe.Subscription) -> Dict:
        """フリープランへの変更処理"""
        customer_id = subscription.customer
        current_time = int(time.time())
        period_end = subscription.current_period_end
        period_start = subscription.current_period_start
        
        used_days = self._calculate_days_from_timestamp(period_start, current_time)
        total_days = self._calculate_days_from_timestamp(period_start, period_end)

        # プロレーション処理を含む即時キャンセル
        canceled_subscription = stripe.Subscription.delete(
            subscription.id,
            prorate=True,
            invoice_now=True
        )

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

    def _calculate_days_from_timestamp(self, start_time: int, end_time: int) -> int:
        """2つのタイムスタンプ間の日数を計算（1日未満は切り上げ）"""
        seconds_diff = end_time - start_time
        days = (seconds_diff + PaymentConfig.SECONDS_PER_DAY - 1) // PaymentConfig.SECONDS_PER_DAY
        return max(1, int(days))

    def _handle_paid_plan_change(self, subscription: stripe.Subscription, 
                               subscription_item: stripe.SubscriptionItem,
                               new_price_id: str, new_account_count: int) -> Dict:
        """有料プラン間の変更処理"""
        if (new_price_id == PaymentConfig.PRICE_ID_BUSINESS and 
            subscription_item.price.product == PaymentConfig.PRODUCT_ID_BUSINESS):
            return self._update_business_plan(subscription, subscription_item, new_account_count)
        else:
            return self._change_to_different_plan(subscription, subscription_item, new_price_id, new_account_count)

    def update_subscription(self, subscription_id: str, new_account_count: int) -> Dict:
        """サブスクリプション更新処理"""
        try:
            subscription = stripe.Subscription.retrieve(
                subscription_id,
                expand=['items.data.price']
            )
            subscription_item = subscription['items']['data'][0]
            
            if subscription_item.price.product != PaymentConfig.PRODUCT_ID_BUSINESS:
                raise PaymentError('ビジネスプランでのみアカウント数を変更できます')

            return self._update_business_plan(
                subscription,
                subscription_item,
                new_account_count
            )
        except stripe.error.StripeError as e:
            self._handle_error('サブスクリプション更新', e, subscription_id=subscription_id)

    def _update_subscription_metadata(self, subscription: stripe.Subscription, new_account_count: int) -> Dict:
        """サブスクリプションのメタデータを更新"""
        updated_subscription = stripe.Subscription.modify(
            subscription.id,
            metadata={
                'account_count': str(new_account_count)
            }
        )
        return self.create_subscription_response(
            updated_subscription,
            updated_subscription.items.data[0].price.id,
            new_account_count,
            message=PaymentConfig.RESPONSE_MESSAGES['account_count_updated']
        )

    def _modify_subscription_item(self, subscription_item_id: str, 
                                new_price: int, product_id: str) -> stripe.Subscription:
        """サブスクリプションアイテムの更新"""
        try:
            return stripe.SubscriptionItem.modify(
                subscription_item_id,
                price_data={
                    'currency': PaymentConfig.CURRENCY,
                    'product': product_id,
                    'unit_amount': new_price,
                    'recurring': {'interval': PaymentConfig.BILLING_INTERVAL}
                },
                proration_behavior='none'
            )
        except stripe.error.InvalidRequestError as e:
            self._log_error(e, {'subscription_item_id': subscription_item_id})
            raise PaymentError('サブスクリプションアイテムの更新に失敗しました')

    def _change_to_free_plan(self, subscription: stripe.Subscription) -> Dict:
        """フリープランへの変更処理"""
        # 現在のサブスクリプションをキャンセル
        stripe.Subscription.delete(subscription.id)
        
        return self.create_subscription_response(
            None,
            PaymentConfig.PRICE_ID_FREE,
            0,
            message=PaymentConfig.RESPONSE_MESSAGES['changed_to_free']
        )