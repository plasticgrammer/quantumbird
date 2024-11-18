<template>
  <v-dialog v-model="isOpen" max-width="900px">
    <v-card rounded="lg">
      <v-card-title class="pb-2">
        <v-icon class="mr-2">mdi-card-account-details-outline</v-icon>
        プラン変更
        <v-btn
          icon="mdi-close"
          variant="text"
          size="small"
          class="float-right"
          @click="closeDialog"
        ></v-btn>
      </v-card-title>
      <v-card-text>
        <!-- プラン選択カード -->
        <div v-if="currentStep === 'plan-selection'" class="px-4 py-0">
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
                <div style="min-height:30px">
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
                </div>

                <!-- 既存のカード内容 -->
                <v-card-title class="text-center pt-2">
                  <div class="text-h6 font-weight-bold">{{ plan.name }}</div>
                </v-card-title>

                <v-card-text>
                  <div class="text-h4 font-weight-bold mb-2 text-center" style="min-height:130px">
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
          
          <v-row justify="center" class="mt-5 mb-1">
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
        </div>

        <!-- 支払い情報フォーム -->
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
                <template v-if="!currentPaymentMethod">
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
              :disabled="isLoading || !formState.selectedPlan"
              @click.prevent="handleSubmit"
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

        <!-- 完了ダイアログ -->
        <v-dialog v-model="showSuccessDialog" max-width="400">
          <v-card rounded="lg">
            <v-card-title class="text-h6">プラン変更完了</v-card-title>
            <v-card-text>
              <div class="my-2">
                {{ dialogMessage || '以下の内容でプランを変更しました。' }}
              </div>
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
                @click="closeDialog"
              >
                閉じる
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, inject, nextTick, reactive, onMounted, onUnmounted, computed } from 'vue'
import { useStore } from 'vuex'
import { useStripe } from '../composables/useStripe'
import { 
  createSubscription,
  getPaymentMethods, 
  changePlan, 
  updatePaymentMethod
} from '../services/paymentService'
import PaymentMethodForm from '../components/PaymentMethodForm.vue'

// 新しく追加するpropsとemits
const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true
  }
})

const emit = defineEmits(['update:modelValue', 'payment-success'])

const isOpen = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const closeDialog = () => {
  showSuccessDialog.value = false
  isOpen.value = false
}

const store = useStore()
const { initializeStripe, cleanup, plans } = useStripe()
const paymentFormRef = ref(null)
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
const dialogMessage = ref('')

// Computed Properties
const currentPlan = computed(() => {
  const subscription = store.getters['auth/currentSubscription']
  if (!subscription || !subscription.planId) return null
  
  const plan = plans.find(p => p.planId === subscription.planId) || plans[0]
  
  return {
    ...plan,
    subscriptionId: subscription.subscriptionId || null,
    currentAccountCount: subscription.accountCount || 0,
    planId: subscription.planId
  }
})

const getCardColor = (plan) => {
  if (formState.selectedPlan === plan.planId) {
    return 'indigo-lighten-1'
  } else if (currentPlan.value?.planId === plan.planId) {
    return 'indigo-lighten-5'
  }
  return ''
}

const handleError = (error) => {
  console.error('Error:', error)
  // エラーメッセージを直接表示
  showError(error.message || 'エラーが発生しました')
}

const resetForm = () => {
  formState.cardName = ''
  errorMessage.value = ''
}

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

    // サブスクリプション情報をより完全な形で更新
    await store.dispatch('auth/updateSubscriptionAttributes', {
      stripeCustomerId: response.subscription.stripeCustomerId,
      planId: formState.selectedPlan,
      accountCount: formState.selectedPlan === 'business' ? formState.accountCount : null,
      subscriptionId: response.subscription.id
    })

    handleSuccess()
  } catch (err) {
    handleError(err)
  }
}

const handleSuccess = async () => {
  showSuccessDialog.value = true
  dialogMessage.value = ''
  resetForm()
  currentStep.value = 'plan-selection'
  emit('payment-success')
}

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
        last4: methods[0].last4,
        expMonth: methods[0].expMonth,
        expYear: methods[0].expYear
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

const handlePlanSelection = async () => {
  try {
    initializingPayment.value = true
    await fetchPaymentMethods()
    currentStep.value = 'payment'
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
  console.log('Validating form:', {
    selectedPlan: formState.selectedPlan,
    accountCount: formState.accountCount,
    currentPlanId: currentPlan.value?.planId,
    currentAccountCount: currentPlan.value?.currentAccountCount
  })

  const errors = []
  if (formState.selectedPlan === 'business' && (!formState.accountCount || formState.accountCount < 1)) {
    errors.push('アカウント数は1以上を指定してください')
  }
  // 同じプランへの変更チェックを削除（必要に応じて）
  return errors
}

const handlePlanChange = async (params) => {
  try {
    isLoading.value = true
    errorMessage.value = ''
    dialogMessage.value = ''

    const response = await changePlan(params)
    
    if (response.message) {
      if (response.subscription?.cancelAt) {
        showSuccessDialog.value = true
        dialogMessage.value = response.message
      } else {
        // Update store before calling handleSuccess
        await store.dispatch('auth/updateSubscriptionAttributes', {
          planId: formState.selectedPlan,
          accountCount: formState.selectedPlan === 'business' ? formState.accountCount : null,
          stripeCustomerId: response.subscription.stripeCustomerId
        })
        handleSuccess()
      }
    }

    return true
  } catch (err) {
    handleError(err)
    return false
  } finally {
    isLoading.value = false
  }
}

const handleSubmit = async () => {
  try {
    const errors = validateForm()
    if (errors.length > 0) {
      showError(errors[0])
      return
    }

    const selectedPlan = plans.find(p => p.planId === formState.selectedPlan)
    if (!selectedPlan) {
      showError('無効なプランが選択されました')
      return
    }

    isLoading.value = true

    // フリープランへの変更
    if (formState.selectedPlan === 'free') {
      try {
        // サブスクリプションIDがある場合のみchangePlanを呼び出し
        if (currentPlan.value?.subscriptionId) {
          const response = await changePlan({
            subscriptionId: currentPlan.value.subscriptionId,
            priceId: 'price_free',
            accountCount: 0
          })
          
          if (response.message) {
            dialogMessage.value = response.message
          }
        }
        
        await store.dispatch('auth/updateSubscriptionAttributes', {
          stripeCustomerId: currentPlan.value?.stripeCustomerId 
        })
        
        handleSuccess()
      } catch (err) {
        handleError(err)
      }
    } else {
      // フリープランからの変更時は常に新規サブスクリプション作成
      const isFromFreePlan = !currentPlan.value?.subscriptionId || currentPlan.value.planId === 'free'
      
      if (isFromFreePlan) {
        console.log('Creating new subscription...')
        // 支払い方法が必要な場合は新規作成
        if (!currentPaymentMethod.value) {
          console.log('Submitting new payment method...')
          const result = await paymentFormRef.value?.submit()
          if (!result?.token) {
            console.log('No token received')
            return
          }
          console.log('Creating subscription with new payment method...')
          await handlePaymentSubmit({ token: result.token })
        } else {
          // 既存の支払い方法があれば再利用
          console.log('Creating subscription with existing payment method...')
          const response = await createSubscription({
            email: store.state.auth.user.email,
            token: null, // 既存の支払い方法を使用
            priceId: selectedPlan.priceId,
            accountCount: formState.selectedPlan === 'business' ? formState.accountCount : 0,
            customerId: store.getters['auth/currentSubscription'].stripeCustomerId
          })
          
          if (response.subscription) {
            await store.dispatch('auth/updateSubscriptionAttributes', {
              stripeCustomerId: response.subscription.stripeCustomerId
            })
            handleSuccess()
          }
        }
      } else {
        // 既存のサブスクリプションがある場合のみプラン変更
        console.log('Changing existing subscription...')
        await handlePlanChange({
          subscriptionId: currentPlan.value.subscriptionId,
          priceId: selectedPlan.priceId,
          accountCount: formState.selectedPlan === 'business' ? formState.accountCount : 0
        })
      }
    }
  } catch (err) {
    console.error('Submit error:', err)
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
  transition: all 0.3s;
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