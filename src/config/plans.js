import store from '@/store'
import { defaultAdvisors } from '../services/bedrockService'

export const plans = [
  {
    planId: 'free',
    priceId: 'price_free',
    name: 'フリープラン',
    price: 0,
    features: ['一部機能の利用制限あり', 'メンバー数最大３名', '基本AIアドバイザーのみ'],
    adminFeatures: {
      maxMembers: 3,
      notifications: false,
      advisorSettings: false,
      accountManagement: false
    },
    systemFeatures: {
      weeklyReportAdvice: true,
      advisors: defaultAdvisors // デフォルトのアドバイザーのみにリセット
    }
  },
  {
    planId: 'pro',
    priceId: 'price_1QJSigJlLYAT4bpznFUNs5eg',
    name: 'プロプラン',
    price: 1000,
    features: ['基本機能が使用可', 'メンバー数最大１０名', '全てのAIアドバイザー'],
    adminFeatures: {
      maxMembers: 10,
      notifications: true,
      advisorSettings: true,
      accountManagement: false
    },
    systemFeatures: {
      weeklyReportAdvice: true
    }
  },
  {
    planId: 'business',
    priceId: 'price_1QJSmjJlLYAT4bpzzPjAgcJj',
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
    systemFeatures: {
      weeklyReportAdvice: true
    }
  }
]

export const getCurrentSubscription = () => store.getters['auth/currentSubscription']

export const getCurrentPlan = () => {
  const subscription = getCurrentSubscription()
  const planId = subscription?.planId || 'free'
  return plans.find(p => p.planId === planId) || plans[0]
}
