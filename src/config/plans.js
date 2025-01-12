import store from '@/store'
import { defaultAdvisors } from '@/services/bedrockService'

// 環境変数からpriceIdを取得（未設定の場合は開発環境用のIDを使用）
const STRIPE_PRO_PRICE_ID = process.env.VUE_APP_STRIPE_PRO_PRICE_ID
const STRIPE_BUSINESS_PRICE_ID = process.env.VUE_APP_STRIPE_BUSINESS_PRICE_ID

/*
 * プラン定義
 * - 管理者機能の制御は adminFeatures にて設定
 * - 組織情報として更新する必要があるものは organizationFeatures にて設定
 */
export const plans = [
  {
    planId: 'free',
    priceId: 'price_free',
    name: 'フリープラン',
    price: 0,
    features: ['利用制限あり（報告通知など）', 'メンバー数最大３名', '基本AIアドバイザーのみ'],
    adminFeatures: {
      maxMembers: 3,
      notifications: false,
      advisorSettings: false,
      accountManagement: false
    },
    organizationFeatures: {
      weeklyReportAdvice: true,
      notifyByEmail: false, // メール通知なしにリセット
      notifySubscriptions: {}, // ブラウザ通知なしにリセット
      advisors: defaultAdvisors // デフォルトのアドバイザーのみにリセット
    }
  },
  {
    planId: 'pro',
    priceId: STRIPE_PRO_PRICE_ID,
    name: 'プロプラン',
    price: 1000,
    features: ['基本機能が使用可', 'メンバー数最大１０名', '全てのAIアドバイザー'],
    adminFeatures: {
      maxMembers: 10,
      notifications: true,
      advisorSettings: true,
      accountManagement: false
    },
    organizationFeatures: {
      weeklyReportAdvice: true
    }
  },
  {
    planId: 'business',
    priceId: STRIPE_BUSINESS_PRICE_ID,
    name: 'ビジネスプラン',
    price: 2000,
    pricePerAccount: 500,
    getPrice: (accountCount) => 2000 + (accountCount * 500),
    priceDescription: ['+ ¥500/アカウント'],
    features: ['基本機能が使用可', 'メンバー数無制限', '全てのAIアドバイザー', 'アカウント管理機能'],
    adminFeatures: {
      maxMembers: -1,
      notifications: true,
      advisorSettings: true,
      accountManagement: true
    },
    organizationFeatures: {
      weeklyReportAdvice: true
    }
  }
]

export const getCurrentSubscription = () => store.getters['auth/currentSubscription']

export const getCurrentPlan = () => {
  // 親組織IDがある場合は子アカウントなのでビジネスプランとして扱う
  const parentOrganizationId = store.getters['auth/parentOrganizationId']
  if (parentOrganizationId) {
    return plans.find(p => p.planId === 'business')
  }

  const subscription = getCurrentSubscription()
  const planId = subscription?.planId || 'free'
  return plans.find(p => p.planId === planId) || plans[0]
}
