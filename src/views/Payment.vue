<template>
  <v-container>
    <v-row dense class="pb-4">
      <v-col>
        <v-btn
          color="primary"
          variant="text"
          @click="router.push({ name: 'AccountSetting' })"
        >
          <v-icon class="mr-2">mdi-arrow-left</v-icon>
          アカウント設定に戻る
        </v-btn>
      </v-col>
    </v-row>

    <v-card class="mx-auto">
      <v-card-title class="text-h5 font-weight-bold text-center pa-4">
        {{ getStepTitle }}
      </v-card-title>

      <!-- プラン選択カード - プラン選択ステップの時のみ表示 -->
      <v-card-text v-if="currentStep === 'plan-selection'">
        <!-- 既存のプラン選択部分をそのまま使用 -->
        <v-row justify="center">
          <v-col
            v-for="plan in plans"
            :key="plan.planId"
            cols="12"
            sm="6"
            md="4"
            class="pa-4"
          >
            <v-card
              :color="getCardColor(plan)"
              :class="[
                'plan-card',
                formState.selectedPlan === plan.planId ? 'selected-plan' : '',
                currentPlan?.planId === plan.planId ? 'current-plan' : ''
              ]"
              class="rounded-lg cursor-pointer position-relative"
              elevation="4"
              @click="formState.selectedPlan = plan.planId"
            >
              <!-- 現在のプランバッジ -->
              <v-chip
                v-if="currentPlan?.planId === plan.planId"
                :color="formState.selectedPlan === plan.planId ? 'white' : 'info'"
                class="current-plan-badge font-weight-bold"
                size="small"
                label
              >
                現在のプラン
              </v-chip>
              <div v-else class="mb-8"></div>

              <!-- 既存のカード内容 -->
              <v-card-title class="text-center pt-2">
                <div class="text-h6 font-weight-bold">{{ plan.name }}</div>
              </v-card-title>

              <v-card-text>
                <div class="text-h4 font-weight-bold mb-2 text-center">
                  <div>
                    ¥{{ plan.price.toLocaleString() }}<span class="text-body-1">/月</span>
                  </div>
                  <template v-if="plan.planId === 'business'">
                    <div class="text-body-1 mb-2">
                      <div v-for="(line, index) in plan.priceDescription" :key="index" class="price-line">
                        {{ line }}
                      </div>
                    </div>
                    <div class="text-subtitle-1 font-weight-regular">
                      アカウント数: {{ formState.accountCount }}
                    </div>
                    <div class="text-h6 mt-2">
                      合計: ¥{{ plan.getPrice(formState.accountCount).toLocaleString() }}<span class="text-body-1">/月</span>
                    </div>
                  </template>
                </div>
                <v-divider class="mb-4"></v-divider>
                <v-list
                  class="bg-transparent"
                  density="compact"
                >
                  <v-list-item
                    v-for="(feature, index) in plan.features"
                    :key="index"
                    :class="formState.selectedPlan === plan.planId ? 'text-white' : ''"
                  >
                    <template #prepend>
                      <v-icon
                        :color="formState.selectedPlan === plan.planId ? 'white' : 'primary'"
                        size="small"
                      >
                        mdi-check-circle
                      </v-icon>
                    </template>
                    {{ feature }}
                  </v-list-item>
                </v-list>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
        
        <!-- プラン選択ボタン部分を修正 -->
        <v-row justify="center" class="mt-4">
          <v-col cols="12" sm="8" md="6">
            <v-btn
              v-if="formState.selectedPlan && formState.selectedPlan !== currentPlan.value?.planId"
              color="primary"
              block
              :loading="initializingPayment"
              :disabled="initializingPayment"
              @click="handlePlanSelection"
            >
              {{ initializingPayment ? '読み込み中...' : '次へ' }}
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>

      <!-- 支払い情報フォーム - 支払いステップの時のみ表示 -->
      <template v-if="currentStep === 'payment'">
        <v-card-text class="px-6 pb-4">
          <!-- 変更内容カード -->
          <v-card class="mb-4 pa-4" variant="outlined">
            <div class="text-subtitle-1 mb-2">変更内容</div>
            <div class="mb-2">
              現在のプラン: {{ currentPlan?.name || 'なし' }}
              <template v-if="currentPlan?.planId === 'business'">
                <div class="mt-1 ml-2">
                  現在のアカウント数: {{ currentPlan.currentAccountCount }}
                  <div>現在の月額料金: ¥{{ currentPlan.getPrice(currentPlan.currentAccountCount).toLocaleString() }}/月</div>
                </div>
              </template>
              <template v-else-if="currentPlan?.planId === 'pro'">
                <div class="mt-1 ml-2">
                  現在の月額料金: ¥{{ currentPlan.price.toLocaleString() }}/月
                </div>
              </template>
            </div>
            <v-divider class="my-3"></v-divider>
            <div>
              変更後のプラン: {{ plans.find(p => p.planId === formState.selectedPlan)?.name }}
              <template v-if="formState.selectedPlan === 'business'">
                <v-text-field
                  v-model="formState.accountCount"
                  type="number"
                  label="アカウント数"
                  class="mt-3 mb-2 ml-2"
                  :rules="validationRules.accountCount"
                  hide-details="auto"
                  density="compact"
                  variant="outlined"
                  max-width="130px"
                  required
                ></v-text-field>
                
                <div class="ml-2">
                  変更後の月額料金: ¥{{ plans.find(p => p.planId === 'business').getPrice(formState.accountCount).toLocaleString() }}/月
                </div>
              </template>
              <template v-if="formState.selectedPlan === 'pro'">
                <div class="mt-1 ml-2">
                  変更後の月額料金: ¥{{ plans.find(p => p.planId === 'pro').price.toLocaleString() }}/月
                </div>
              </template>
            </div>
          </v-card>

          <!-- 支払い方法セクション -->
          <template v-if="formState.selectedPlan === 'pro' || formState.selectedPlan === 'business'">
            <v-card class="mb-4 pa-4" variant="outlined">
              <h3 class="text-h6 mb-4">支払い方法</h3>

              <!-- 新規支払い方法入力フォーム -->
              <template v-if="!currentPaymentMethod || !isSubscriptionActive.value">
                <PaymentMethodForm
                  ref="paymentFormRef"
                  :element-id="'payment-form'"
                  :loading="isLoading"
                  :show-submit-button="false"
                  @error="errorMessage = $event"
                />
              </template>

              <!-- 支払い方法更新フォーム -->
              <template v-else-if="isPaymentMethodUpdateMode">
                <PaymentMethodForm
                  element-id="payment-update"
                  :loading="isUpdatingPayment"
                  :show-submit-button="true"
                  @submit="handlePaymentMethodOnlyUpdate"
                  @error="errorMessage = $event"
                >
                  <template #submit-button>
                    <div class="d-flex gap-2 pt-2">
                      <v-btn
                        color="primary"
                        type="submit"
                        :loading="isUpdatingPayment"
                      >
                        支払い方法を更新
                      </v-btn>
                      <span class="mx-2"></span>
                      <v-btn
                        variant="outlined"
                        @click="isPaymentMethodUpdateMode = false"
                      >
                        キャンセル
                      </v-btn>
                    </div>
                  </template>
                </PaymentMethodForm>
              </template>

              <!-- 現在の支払い方法表示 -->
              <template v-else>
                <div class="mb-4">
                  <div class="d-flex align-center justify-space-between">
                    <div class="d-flex align-center">
                      <v-icon class="mr-2">mdi-credit-card</v-icon>
                      <span>**** **** **** {{ currentPaymentMethod.last4 }}</span>
                      <span class="ml-2 text-caption">
                        有効期限: {{ String(currentPaymentMethod.expMonth).padStart(2, '0') }}/{{ String(currentPaymentMethod.expYear).slice(-2) }}
                      </span>
                    </div>
                    <v-btn
                      variant="text"
                      color="primary"
                      @click="isPaymentMethodUpdateMode = true"
                    >
                      支払い方法を変更
                    </v-btn>
                  </div>
                </div>
              </template>
            </v-card>
          </template>

          <!-- プラン変更確認ボタン - 支払い方法更新モード時は非表示 -->
          <v-btn
            v-if="!isPaymentMethodUpdateMode"
            color="primary"
            block
            size="large"
            :loading="isLoading"
            :disabled="isLoading"
            @click="handleSubmit"
          >
            {{ isLoading ? '処理中...' : formState.selectedPlan === 'free' ? 'プランを解約する' : 'プランを変更する' }}
          </v-btn>
        </v-card-text>

        <v-card-text class="px-6 py-4">
          <v-btn
            variant="outlined"
            @click="currentStep = 'plan-selection'"
          >
            プラン選択に戻る
          </v-btn>
        </v-card-text>
      </template>
    </v-card>

    <!-- 完了ダイアログ -->
    <v-dialog v-model="showSuccessDialog" max-width="400">
      <v-card>
        <v-card-title class="text-h6">プラン変更完了</v-card-title>
        <v-card-text>
          <div class="my-2">以下の内容でプランを変更しました。</div>
          <v-card variant="outlined" class="pa-3">
            <div class="text-subtitle-1 font-weight-bold mb-2">
              {{ plans.find(p => p.planId === formState.selectedPlan)?.name }}
            </div>
            <template v-if="formState.selectedPlan === 'business'">
              <div class="text-body-1">
                アカウント数: {{ formState.accountCount }}
              </div>
              <div class="text-body-1">
                月額料金: ¥{{ plans.find(p => p.planId === 'business').getPrice(formState.accountCount).toLocaleString() }}/月
              </div>
            </template>
            <template v-else-if="formState.selectedPlan === 'pro'">
              <div class="text-body-1">
                月額料金: ¥{{ plans.find(p => p.planId === 'pro').price.toLocaleString() }}/月
              </div>
            </template>
            <template v-else>
              <div class="text-body-1">
                無料
              </div>
            </template>
          </v-card>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="primary"
            text
            @click="showSuccessDialog = false"
          >
            閉じる
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, inject, nextTick, reactive, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { useStripe } from '../composables/useStripe'
import { 
  createSubscription, 
  getPaymentMethods, 
  changePlan, 
  updatePaymentMethod 
} from '../services/paymentService'
import PaymentMethodForm from '../components/PaymentMethodForm.vue'

const router = useRouter()
const store = useStore()
const { initializeStripe, cleanup, plans } = useStripe()
const paymentFormRef = ref(null)
const emit = defineEmits(['payment-success'])
const showError = inject('showError')

// States
const formState = reactive({
  cardName: '',
  selectedPlan: null,
  accountCount: 1,
  validation: {
    accountCount: []
  }
})

const validationRules = {
  accountCount: [
    v => !!v || 'アカウント数は必須です',
    v => v > 0 || 'アカウント数は1以上を指定してください',
    v => Number.isInteger(Number(v)) || '整数を入力してください'
  ]
}

const currentPaymentMethod = ref(null)
const isLoading = ref(false)
const errorMessage = ref('')
const showSuccessDialog = ref(false)
const isUpdatingPayment = ref(false)
const isPaymentMethodUpdateMode = ref(false)
const currentStep = ref('plan-selection')
const abortController = new AbortController()
const initializingPayment = ref(false)

// Computed Properties
const currentPlan = computed(() => {
  const subscription = store.getters['auth/currentSubscription']
  if (!subscription) return null
  
  const plan = plans.find(p => p.planId === subscription.planId) || plans[0]
  
  return {
    ...plan,
    subscriptionId: subscription.subscriptionId,
    currentAccountCount: subscription.accountCount
  }
})

const needsPaymentMethod = computed(() => {
  if (formState.selectedPlan === 'free') return false
  if (!currentPaymentMethod.value) return true
  return currentPlan.value?.planId === 'free' && 
         ['pro', 'business'].includes(formState.selectedPlan)
})

const getStepTitle = computed(() => currentStep.value === 'payment' ? 'プラン変更' : 'プラン選択')

const getCardColor = (plan) => {
  if (formState.selectedPlan === plan.planId) {
    return 'indigo-lighten-1'
  } else if (currentPlan.value?.planId === plan.planId) {
    return 'indigo-lighten-5'
  }
  return ''
}

const isSubscriptionActive = computed(() => {
  const subscription = store.getters['auth/currentSubscription']
  return subscription?.status === 'active'
})

const handleError = (error, customMessage = '処理に失敗しました') => {
  console.error(error)
  errorMessage.value = error.message || customMessage
}

const resetForm = () => {
  formState.cardName = ''
  errorMessage.value = ''
}

// fetchPaymentMethodsを修正
const fetchPaymentMethods = async () => {
  const user = store.state.auth.user
  if (!user) return

  try {
    console.log('Fetching payment methods...')
    const response = await getPaymentMethods(user.email, { 
      signal: abortController.signal 
    })
    console.log('Payment methods response:', response)
    const methods = response?.data?.paymentMethods || []
    if (methods.length > 0) {
      currentPaymentMethod.value = {
        last4: methods[0].card.last4,
        expMonth: methods[0].card.exp_month,
        expYear: methods[0].card.exp_year
      }
      console.log('Current payment method set:', currentPaymentMethod.value)
    } else {
      currentPaymentMethod.value = null
    }
  } catch (error) {
    console.error('Error fetching payment methods:', error)
    if (!error.name === 'AbortError') {
      showError('支払い方法の取得に失敗しました')
    }
  }
}

// handlePaymentSubmitメソッドを修正
const handlePaymentSubmit = async ({ token }) => {
  try {
    const selectedPlan = plans.find(p => p.planId === formState.selectedPlan)
    const userEmail = store.state.auth.user.email
    
    const response = await createSubscription({
      email: userEmail,
      token: token.id,
      priceId: selectedPlan.priceId,
      accountCount: formState.selectedPlan === 'business' ? formState.accountCount : 0
    })
    const subscription = response.subscription

    await store.dispatch('auth/updateSubscriptionAttributes', {
      planId: selectedPlan.planId,
      accountCount: formState.selectedPlan === 'business' ? formState.accountCount : 0,
      subscriptionId: subscription.id,
      status: subscription.status
    })

    showSuccessDialog.value = true
    resetForm()
    currentStep.value = 'plan-selection'
    emit('payment-success')
    
  } catch (err) {
    handleError(err)
  }
}

const handlePlanSelection = async () => {
  try {
    initializingPayment.value = true
    currentStep.value = 'payment'
    await fetchPaymentMethods()
  } catch (error) {
    showError('支払い情報の取得に失敗しました')
    currentStep.value = 'plan-selection'
  } finally {
    initializingPayment.value = false
  }
}

const handlePaymentMethodOnlyUpdate = async ({ token }) => {
  try {
    isUpdatingPayment.value = true
    errorMessage.value = ''

    await updatePaymentMethod({ token: token.id })
    await fetchPaymentMethods()
    
    isPaymentMethodUpdateMode.value = false
    showSuccessDialog.value = true
  } catch (err) {
    showError('支払い方法の更新に失敗しました')
  } finally {
    isUpdatingPayment.value = false
  }
}

const validateForm = () => {
  const errors = []
  if (formState.selectedPlan === 'business' && (!formState.accountCount || formState.accountCount < 1)) {
    errors.push('アカウント数は1以上を指定してください')
  }
  if (formState.selectedPlan === currentPlan.value?.planId &&
      formState.accountCount === currentPlan.value?.currentAccountCount) {
    errors.push('現在のプランと同じです')
  }
  return errors
}

const handleSubmit = async () => {
  try {
    console.log('handleSubmit start', {
      selectedPlan: formState.selectedPlan,
      isActive: isSubscriptionActive.value,
      needsPayment: needsPaymentMethod.value
    })
    
    isLoading.value = true
    errorMessage.value = ''

    const selectedPlan = plans.find(p => p.planId === formState.selectedPlan)
    if (!selectedPlan) {
      throw new Error('無効なプランが選択されました')
    }

    const errors = validateForm()
    if (errors.length > 0) {
      throw new Error(errors[0])
    }

    // フリープランへの変更
    if (formState.selectedPlan === 'free') {
      console.log('Changing to free plan')
      if (!currentPlan.value?.subscriptionId) {
        throw new Error('サブスクリプションIDが見つかりません')
      }
      
      const response = await changePlan({
        subscriptionId: currentPlan.value.subscriptionId,
        priceId: selectedPlan.priceId,
        accountCount: 0
      })

      await store.dispatch('auth/updateSubscriptionAttributes', {
        planId: selectedPlan.planId,
        accountCount: 0,
        subscriptionId: currentPlan.value.subscriptionId,
        status: response.subscription.status
      })
    } else {
      // 有料プランへの変更
      if (needsPaymentMethod.value || !isSubscriptionActive.value) {
        console.log('Need new payment method or subscription')
        console.log('Payment form ref:', paymentFormRef.value)

        // フォームの存在確認を改善
        await nextTick()
        if (!paymentFormRef.value) {
          throw new Error('支払いフォームの準備ができていません。ページを更新してお試しください。')
        }

        const result = await paymentFormRef.value.submit()
        console.log('Payment form submit result:', result)
        
        if (!result?.token) {
          throw new Error('支払い情報の取得に失敗しました')
        }
        
        // 新規サブスクリプション作成
        await handlePaymentSubmit({ token: result.token })
      } else {
        console.log('Updating existing subscription')
        if (!currentPlan.value?.subscriptionId) {
          throw new Error('サブスクリプションIDが見つかりません')
        }

        const response = await changePlan({
          subscriptionId: currentPlan.value.subscriptionId,
          priceId: selectedPlan.priceId,
          accountCount: formState.selectedPlan === 'business' ? formState.accountCount : 0
        })

        await store.dispatch('auth/updateSubscriptionAttributes', {
          planId: selectedPlan.planId,
          accountCount: formState.selectedPlan === 'business' ? formState.accountCount : 0,
          subscriptionId: currentPlan.value.subscriptionId,
          status: response.subscription.status
        })
      }
    }

    showSuccessDialog.value = true
    resetForm()
    currentStep.value = 'plan-selection'
    emit('payment-success')

  } catch (err) {
    console.error('Plan change error:', err)
    showError(err.message || '処理に失敗しました')
  } finally {
    isLoading.value = false
  }
}

// Lifecycle Hooks
onMounted(async () => {
  try {
    await nextTick()
    const { stripe, error } = await initializeStripe()
    if (error || !stripe) {
      throw new Error(error || 'Stripe initialization failed')
    }

    const user = store.state.auth.user
    if (user) {
      formState.email = user.email
      formState.selectedPlan = store.getters['auth/currentSubscription'].planId
    } else {
      formState.selectedPlan = 'free'
    }

    if (currentPlan.value) {
      formState.accountCount = currentPlan.value.planId === 'business' 
        ? currentPlan.value.currentAccountCount 
        : 1
    }
  } catch (error) {
    if (!error.name === 'AbortError') {
      handleError(error, '初期化に失敗しました')
    }
  }
})

onUnmounted(() => {
  abortController.abort()
  cleanup()
})
</script>

<style scoped>
.v-list-item--density-compact.v-list-item--one-line {
  min-height: auto;
}

.plan-card {
  height: 100%;
  border: 1px solid currentColor;
  position: relative;
}

.stripe-element {
  min-height: 40px;
  background-color: white;
}

.stripe-element:empty {
  background-color: white;
}

.price-line {
  line-height: 1.6;
}

.v-list-item--density-compact.v-list-item--one-line {
  min-height: auto;
}
</style>