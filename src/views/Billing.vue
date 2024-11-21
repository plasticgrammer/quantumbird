<template>
  <v-container>
    <v-row dense class="pb-4">
      <v-col>
        <h3>
          <v-icon size="large" class="mr-1">mdi-currency-usd</v-icon>
          支払い設定
        </h3>
      </v-col>
    </v-row>

    <!-- プラン変更ダイアログ -->
    <PaymentDialog
      v-model="showPlanSelector"
      @payment-success="handlePaymentSuccess"
    />

    <!-- 現在のプラン情報 -->
    <v-card>
      <v-card-title>現在のプラン</v-card-title>
      <v-card-text>
        <v-row align="center">
          <v-col>
            <div class="text-h6 font-weight-bold">{{ currentPlanName }}</div>
            <p class="text-body-1 mt-2 px-4">
              <span v-if="currentPlanPrice === 0">無料</span>
              <span v-else>{{ currentPlanPrice }}円/月</span>
            </p>
            <p v-if="currentSubscription?.accountCount > 0" class="text-caption  px-4">
              アカウント数: {{ currentSubscription.accountCount }}
            </p>
          </v-col>
          <v-col cols="auto">
            <v-btn color="primary" @click="showPlanSelector = true">
              プランを変更
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- 請求履歴 -->
    <v-card class="mt-4">
      <v-card-title>請求履歴</v-card-title>
      <v-card-text>
        <v-table v-if="invoices.length > 0">
          <thead>
            <tr>
              <th>日付</th>
              <th>内容</th>
              <th>金額</th>
              <th class="text-center">ステータス</th>
              <th class="text-center">請求書</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="invoice in invoices" :key="invoice.id">
              <td>{{ formatDate(invoice.date) }}</td>
              <td>{{ invoice.description }}</td>
              <td :class="{ 'text-error': invoice.amount < 0 }">
                {{ formatAmount(invoice.amount) }}
              </td>
              <td class="text-center">
                <v-chip
                  :color="getStatusColor(invoice)"
                  size="small"
                >
                  {{ getStatusText(invoice) }}
                </v-chip>
              </td>
              <td class="text-center">
                <v-btn
                  v-if="invoice.url"
                  variant="text"
                  size="large"
                  color="primary"
                  @click="openInvoice(invoice.url)"
                >
                  <v-icon size="large">mdi-open-in-new</v-icon>
                </v-btn>
              </td>
            </tr>
          </tbody>
        </v-table>
        <div v-else class="text-center py-4">
          <p class="text-body-1 text-medium-emphasis">
            {{ isLoading ? '読み込み中...' : '請求履歴がありません' }}
          </p>
        </div>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useStripe } from '../composables/useStripe'
import { getInvoices } from '../services/paymentService'
import PaymentDialog from '../components/PaymentDialog.vue'

const store = useStore()
const { plans } = useStripe()

// 状態の追加
const isLoading = ref(false)
const error = ref(null)
const invoices = ref([])
const showPlanSelector = ref(false)

const currentSubscription = computed(() => store.getters['auth/currentSubscription'])

const currentPlanName = computed(() => {
  if (!currentSubscription.value?.planId) return 'フリープラン'
  const plan = plans.find(p => p.planId === currentSubscription.value.planId)
  return plan?.name || 'フリープラン'
})

const currentPlanPrice = computed(() => {
  if (!currentSubscription.value?.planId) return 0
  const plan = plans.find(p => p.planId === currentSubscription.value.planId)
  if (!plan) return 0
  
  return plan.planId === 'business' && currentSubscription.value.accountCount
    ? plan.getPrice(currentSubscription.value.accountCount)
    : plan.price || 0
})

const fetchInvoices = async (customerId) => {
  try {
    isLoading.value = true
    error.value = null
    
    // 顧客IDがあれば請求履歴を取得
    if (currentSubscription.value?.stripeCustomerId) {
      const response = await getInvoices(customerId)
      invoices.value = response.data.invoices
    } else {
      invoices.value = []
    }
  } catch (err) {
    error.value = '請求履歴の取得に失敗しました'
    console.error('Failed to fetch invoices:', err)
    invoices.value = []
  } finally {
    isLoading.value = false
  }
}

const formatDate = (timestamp) => {
  const date = new Date(timestamp * 1000)  // UnixタイムスタンプをDateオブジェクトに変換
  const options = { year: 'numeric', month: '2-digit', day: '2-digit' }
  return date.toLocaleDateString('ja-JP', options)
}

const formatAmount = (amount) => {
  const prefix = amount < 0 ? '-' : ''
  return `${prefix}${Math.abs(amount).toLocaleString()}円`
}

const getStatusColor = (invoice) => {
  if (invoice.type === 'refund') return 'info'
  return invoice.status === 'paid' ? 'success' : 'warning'
}

const getStatusText = (invoice) => {
  if (invoice.type === 'refund') return '返金済み'
  return invoice.status === 'paid' ? '支払い済み' : '未払い'
}

const handlePaymentSuccess = async () => {
  if (currentSubscription.value?.stripeCustomerId) {
    await fetchInvoices(currentSubscription.value.stripeCustomerId)
  }
}

const openInvoice = (url) => {
  if (url) {
    window.open(url, '_blank')
  }
}

onMounted(async () => {
  try {
    // 非同期でStripe情報を取得
    if (currentSubscription.value?.stripeCustomerId) {
      await fetchInvoices(currentSubscription.value.stripeCustomerId)
    }
  } catch (error) {
    console.error('Failed to initialize billing view:', error)
  }
})
</script>

<style>
.text-error {
  color: var(--v-error-base);
}
</style>