import store from '@/store'

export const plans = [
  {
    planId: 'free',
    priceId: 'price_free',
    name: 'フリープラン',
    price: 0,
    features: ['基本機能が使用可', 'メンバー数最大5名', 'AIアドバイスが利用不可'],
    adminFeatures: {
      maxMembers: 5,
      accountManagement: false
    },
    systemFeatures: {
      weeklyReportAdvice: false
    }
  },
  {
    planId: 'pro',
    priceId: 'price_1QJSigJlLYAT4bpznFUNs5eg',
    name: 'プロプラン',
    price: 1000,
    features: ['基本機能が使用可', 'メンバー数無制限', 'AIアドバイスが利用可'],
    adminFeatures: {
      maxMembers: -1,
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
    features: [
      '基本機能が使用可',
      'アカウント管理機能',
      'メンバー数無制限',
      'AIアドバイスが利用可'
    ],
    adminFeatures: {
      maxMembers: -1,
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