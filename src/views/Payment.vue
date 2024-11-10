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
        プラン選択
      </v-card-title>

      <!-- プラン選択カード -->
      <v-card-text>
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
                color="primary"
                class="current-plan-badge font-weight-bold"
                size="small"
                label
              >
                現在のプラン
              </v-chip>

              <!-- 既存のカード内容 -->
              <v-card-title class="text-center pt-6">
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
                      選択アカウント数: {{ formState.accountCount }}
                    </div>
                    <div class="text-h5 mt-2">
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
      </v-card-text>

      <!-- 支払い情報フォーム -->
      <v-card-text 
        v-show="showPaymentForm"
        class="px-6 py-4"
      >
        <v-divider class="mb-4"></v-divider>
        <v-row class="d-flex justify-center">
          <v-col cols="8">
            <h3 class="text-h6 mb-4">支払い情報の入力</h3>
            <v-form ref="formRef" @submit.prevent="handleSubmit">
              <!-- メールアドレス -->
              <v-text-field
                v-model="formState.email"
                label="メールアドレス"
                :rules="validationRules.email"
                required
              ></v-text-field>

              <!-- カード所有者名 -->
              <v-text-field
                v-model="formState.cardName"
                label="カード名義"
                :rules="validationRules.cardName"
                required
              ></v-text-field>

              <!-- ビジネスプラン用のアカウント数入力フィールド -->
              <v-text-field
                v-if="formState.selectedPlan === 'business'"
                v-model="formState.accountCount"
                max-width="200px"
                type="number"
                label="アカウント数"
                :rules="validationRules.accountCount"
                required
                :hint="`月額料金: ¥${plans.find(p => p.planId === 'business').getPrice(formState.accountCount).toLocaleString()}/月`"
                persistent-hint
              ></v-text-field>

              <!-- Stripe Elements マウントポイント -->
              <div class="mt-4">
                <label class="text-subtitle-1">カード情報</label>
                <div
                  id="card-element"
                  class="mt-2 pa-4 stripe-element"
                  style="min-height: 40px"
                ></div>
                <div
                  v-if="errorMessage"
                  id="card-errors"
                  class="error--text mt-2"
                >
                  {{ errorMessage }}
                </div>
              </div>

              <!-- 支払いボタン -->
              <v-btn
                type="submit"
                color="primary"
                class="mt-6"
                block
                size="large"
                :loading="isLoading"
                :disabled="isLoading"
              >
                {{ isLoading ? '処理中...' : '支払いを確定する' }}
              </v-btn>
            </v-form>
          </v-col>
        </v-row>
      </v-card-text>

      <!-- プラン変更確認セクション -->
      <v-card-text 
        v-if="showPlanChangeConfirm"
        class="px-6 py-4"
      >
        <v-divider class="mb-4"></v-divider>
        <v-row class="d-flex justify-center">
          <v-col cols="8">
            <h3 class="text-h6 mb-4">プラン変更の確認</h3>
            
            <!-- 変更内容カード -->
            <v-card class="mb-4 pa-4" variant="outlined">
              <div class="text-subtitle-1 mb-2">変更内容</div>
              <div>変更後のプラン: {{ plans.find(p => p.planId === formState.selectedPlan)?.name }}</div>
              <template v-if="formState.selectedPlan === 'business'">
                <div class="mt-4">
                  <v-text-field
                    v-model="formState.accountCount"
                    type="number"
                    label="アカウント数"
                    :rules="validationRules.accountCount"
                    :hint="`月額料金: ¥${plans.find(p => p.planId === 'business').getPrice(formState.accountCount).toLocaleString()}/月`"
                    persistent-hint
                    required
                  ></v-text-field>
                </div>
                <div class="mt-2">変更後の月額料金: ¥{{ plans.find(p => p.planId === 'business').getPrice(formState.accountCount).toLocaleString() }}/月</div>
              </template>
            </v-card>

            <!-- 支払い情報カード -->
            <v-card class="mb-4 pa-4" variant="outlined">
              <div class="d-flex justify-space-between align-center">
                <div class="text-subtitle-1">支払い方法</div>
                <v-btn
                  v-if="!showPaymentMethodForm"
                  variant="text"
                  color="primary"
                  @click="showPaymentMethodForm = true"
                >
                  変更する
                </v-btn>
              </div>
              
              <!-- 現在の支払い方法表示 -->
              <template v-if="!showPaymentMethodForm">
                <div class="mt-2" v-if="currentPaymentMethod">
                  <div class="d-flex align-center">
                    <v-icon class="mr-2">mdi-credit-card</v-icon>
                    <span>**** **** **** {{ currentPaymentMethod.last4 }}</span>
                  </div>
                  <div class="text-caption">
                    有効期限: {{ String(currentPaymentMethod.expMonth).padStart(2, '0') }}/{{ String(currentPaymentMethod.expYear).slice(-2) }}
                  </div>
                </div>
              </template>

              <!-- 支払い方法変更フォーム -->
              <v-form
                v-else
                ref="paymentMethodFormRef"
                @submit.prevent="handlePaymentMethodUpdate"
                class="mt-4"
              >
                <v-text-field
                  v-model="paymentMethodForm.cardName"
                  label="カード名義"
                  :rules="validationRules.cardName"
                  required
                ></v-text-field>

                <div class="mt-4">
                  <label class="text-subtitle-1">カード情報</label>
                  <div
                    id="card-element-update"
                    class="mt-2 pa-4 stripe-element"
                    style="min-height: 40px"
                  ></div>
                  <div
                    v-if="paymentMethodError"
                    class="error--text mt-2"
                  >
                    {{ paymentMethodError }}
                  </div>
                </div>

                <div class="d-flex gap-2 mt-4">
                  <v-btn
                    color="primary"
                    type="submit"
                    :loading="isUpdatingPaymentMethod"
                  >
                    支払い方法を更新
                  </v-btn>
                  <v-btn
                    variant="outlined"
                    @click="showPaymentMethodForm = false"
                  >
                    キャンセル
                  </v-btn>
                </div>
              </v-form>
            </v-card>
            
            <v-btn
              color="primary"
              block
              size="large"
              :loading="isLoading"
              :disabled="isLoading"
              @click="handleSubmit"
            >
              {{ isLoading ? '処理中...' : 'プランを変更する' }}
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>

      <!-- プラン変更セクション -->
      <v-card-text v-if="currentPlan && currentPlan.planId === 'business'" class="mt-4">
        <v-divider class="mb-6"></v-divider>
        <h3 class="text-h6 mb-4">アカウント数の変更</h3>
        
        <!-- 現在のプラン情報 -->
        <v-card class="mb-4 pa-4" variant="outlined">
          <div class="text-subtitle-1 mb-2">現在のプラン情報</div>
          <div>現在のアカウント数: {{ currentPlan.currentAccountCount }}アカウント</div>
          <div>現在の月額料金: ¥{{ currentPlan.getPrice(currentPlan.currentAccountCount).toLocaleString() }}/月</div>
        </v-card>

        <!-- アカウント数変更フォーム -->
        <v-form ref="accountUpdateFormRef" @submit.prevent="handleAccountUpdate">
          <v-text-field
            v-model="accountUpdateForm.newAccountCount"
            type="number"
            label="新しいアカウント数"
            :rules="validationRules.accountCount"
            :hint="`変更後の月額料金: ¥${currentPlan.getPrice(accountUpdateForm.newAccountCount).toLocaleString()}/月`"
            persistent-hint
            required
          ></v-text-field>

          <v-btn
            type="submit"
            color="primary"
            class="mt-4"
            block
            :loading="isUpdating"
            :disabled="isUpdating || accountUpdateForm.newAccountCount == currentPlan.currentAccountCount"
          >
            {{ isUpdating ? '更新中...' : 'アカウント数を変更する' }}
          </v-btn>
        </v-form>
      </v-card-text>
    </v-card>

    <!-- 完了ダイアログ -->
    <v-dialog v-model="showSuccessDialog" max-width="400">
      <v-card>
        <v-card-title>支払い完了</v-card-title>
        <v-card-text>支払い処理が正常に完了しました。</v-card-text>
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
import { ref, nextTick, reactive, onMounted, onUnmounted, computed } from 'vue'
import { useStripe } from '../composables/useStripe'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { createSubscription, updateSubscription, getPaymentMethods, changePlan } from '../services/paymentService'

const router = useRouter()
const store = useStore()
const emit = defineEmits(['payment-success']) // emitを定義

// プラン情報を定義
const plans = [
  { 
    planId: 'free', // 表示制御用のID
    priceId: 'price_free', // Stripeの価格ID
    name: 'フリープラン',
    price: 0,
    features: ['基本機能が使用可能', '最大5名まで登録可能']
  },
  { 
    planId: 'pro',
    priceId: 'price_1QJSigJlLYAT4bpznFUNs5eg',
    name: 'プロプラン',
    price: 1000,
    features: ['全機能が使用可能', 'メンバー数無制限']
  },
  {
    planId: 'business',
    priceId: 'price_1QJSmjJlLYAT4bpzzPjAgcJj',
    name: 'ビジネスプラン',
    price: 2000,
    pricePerAccount: 300,
    getPrice: (accountCount) => 2000 + (accountCount * 300),
    priceDescription: [
      '+ ¥300/アカウント'
    ],
    features: [
      '全機能が使用可能',
      'アカウント管理機能',
      '請求書発行対応'
    ]
  }
]

// カードの色を決定する関数
const getCardColor = (plan) => {
  if (currentPlan.value?.planId === plan.planId && formState.selectedPlan === plan.planId) {
    return 'blue-darken-1' // 現在のプランかつ選択中
  }
  if (currentPlan.value?.planId === plan.planId) {
    return 'blue-lighten-4' // 現在のプラン
  }
  if (formState.selectedPlan === plan.planId) {
    return 'blue-accent-2' // 選択中
  }
  return '' // デフォルト
}

const formRef = ref(null)
const { initializeStripe, createToken, card } = useStripe()

const formState = reactive({
  email: '',
  cardName: '',
  selectedPlan: null,
  accountCount: 1
})

const validationRules = {
  email: [
    v => !!v || 'メールアドレスは必須です',
    v => /.+@.+\..+/.test(v) || '有効なメールアドレスを入力してください'
  ],
  cardName: [
    v => !!v || 'カード名義は必須です'
  ],
  plan: [
    v => !!v || 'プランを選択してください'
  ],
  accountCount: [
    v => !!v || 'アカウント数は必須です',
    v => v > 0 || 'アカウント数は1以上である必要があります',
    v => Number.isInteger(Number(v)) || '整数を入力してください'
  ]
}

const isLoading = ref(false)
const errorMessage = ref('')
const showSuccessDialog = ref(false)

// resetForm関数を定義
const resetForm = () => {
  formState.email = ''
  formState.cardName = ''
  formState.selectedPlan = null
  formState.accountCount = 1 // 追加：アカウント数のリセット
  errorMessage.value = ''
  if (formRef.value) {
    formRef.value.reset()
  }
}

// 現在のプラン情報を取得
const currentPlan = computed(() => {
  const subscription = store.getters['auth/currentSubscription']
  const plan = plans.find(p => p.priceId === subscription.planId) || plans[0]
  
  return {
    ...plan,
    currentAccountCount: subscription.accountCount
  }
})

// 支払い方法の状態を追加
const hasPaymentMethod = ref(false)
const isNewCustomer = computed(() => !hasPaymentMethod.value)

// 支払い情報フォームの表示条件を変更
const showPaymentForm = computed(() => {
  return (formState.selectedPlan === 'pro' || formState.selectedPlan === 'business') && isNewCustomer.value
})

// プラン変更確認セクションの表示条件を修正
const showPlanChangeConfirm = computed(() => {
  if (!formState.selectedPlan || isNewCustomer.value) return false
  if (formState.selectedPlan === currentPlan.value?.planId) return false
  return true
})

// フォーム送信処理
const handleSubmit = async () => {
  const form = formRef.value
  if (!form) return
  
  const { valid } = await form.validate()
  if (!valid) return

  isLoading.value = true
  errorMessage.value = ''

  try {
    const selectedPlan = plans.find(p => p.planId === formState.selectedPlan)
    
    if (isNewCustomer.value) {
      // 新規顧客の場合
      const { token, error } = await createToken({
        name: formState.cardName
      })

      if (error) throw new Error(error.message)

      await createSubscription({
        email: formState.email,
        token: token.id,
        planId: selectedPlan.priceId,
        accountCount: formState.selectedPlan === 'business' ? formState.accountCount : 0
      })
    } else {
      // 既存顧客のプラン変更
      await changePlan({
        subscriptionId: currentPlan.value.subscriptionId,
        planId: selectedPlan.priceId,
        accountCount: formState.selectedPlan === 'business' ? formState.accountCount : 0
      })
    }

    // 成功時の処理
    showSuccessDialog.value = true
    resetForm()
    emit('payment-success')
    await store.dispatch('auth/fetchUser')

  } catch (err) {
    errorMessage.value = err.message || '処理に失敗しました'
  } finally {
    isLoading.value = false
  }
}

// アカウント数更新用の状態
const accountUpdateFormRef = ref(null)
const isUpdating = ref(false)
const accountUpdateForm = reactive({
  newAccountCount: 1
})

// アカウント数更新処理
const handleAccountUpdate = async () => {
  const form = accountUpdateFormRef.value
  if (!form) return
  
  const { valid } = await form.validate()
  if (!valid) return

  isUpdating.value = true

  try {
    // アカウント数更新APIの呼び出し
    await updateSubscription({
      newAccountCount: accountUpdateForm.newAccountCount,
      subscriptionId: currentPlan.value.subscriptionId // subscriptionIdを追加
    })

    // 成功時の処理
    showSuccessDialog.value = true
    await store.dispatch('auth/fetchUser')

  } catch (err) {
    errorMessage.value = err.message || 'アカウント数の更新に失敗しました'
  } finally {
    isUpdating.value = false
  }
}

const currentPaymentMethod = ref(null)
const showPaymentMethodForm = ref(false)
const paymentMethodFormRef = ref(null)
const isUpdatingPaymentMethod = ref(false)
const paymentMethodError = ref('')
const paymentMethodForm = reactive({
  cardName: ''
})

// 支払い方法更新用のStripeカード要素
const updateCardElement = ref(null)

const handlePaymentMethodUpdate = async () => {
  const form = paymentMethodFormRef.value
  if (!form) return
  
  const { valid } = await form.validate()
  if (!valid) return

  isUpdatingPaymentMethod.value = true
  paymentMethodError.value = ''

  try {
    const { token, error } = await createToken({
      name: paymentMethodForm.cardName
    })

    if (error) throw new Error(error.message)

    // 支払い方法更新APIの呼び出し
    await updatePaymentMethod({
      token: token.id
    })

    // 支払い方法の再取得
    await fetchPaymentMethods()
    showPaymentMethodForm.value = false

  } catch (err) {
    paymentMethodError.value = err.message || '支払い方法の更新に失敗しました'
  } finally {
    isUpdatingPaymentMethod.value = false
  }
}

// 支払い方法取得関数
const fetchPaymentMethods = async () => {
  const user = store.state.auth.user
  if (user) {
    try {
      const response = await getPaymentMethods(user.email)
      const methods = response?.data?.paymentMethods || []
      currentPaymentMethod.value = methods[0]
      hasPaymentMethod.value = methods.length > 0
    } catch (error) {
      console.error('支払い方法の取得に失敗しました:', error)
    }
  }
}

onMounted(async () => {
  try {
    await nextTick()
    await initializeStripe()
    
    if (card.value) {
      card.value.on('change', function(event) {
        if (event.error) {
          errorMessage.value = event.error.message
        } else {
          errorMessage.value = ''
        }
      })
    }

    // 支払い方法の確認を修正
    const user = store.state.auth.user
    if (user) {
      try {
        const response = await getPaymentMethods(user.email)
        // レスポンスの構造に合わせて修正
        const methods = response?.data?.paymentMethods || []
        hasPaymentMethod.value = methods.length > 0
        
        // デバッグ用（必要に応じて削除）
        console.log('Payment methods:', methods)
      } catch (error) {
        console.error('支払い方法の取得に失敗しました:', error)
        hasPaymentMethod.value = false
      }
    }
  } catch (error) {
    console.error('Failed to initialize:', error)
    errorMessage.value = '初期化に失敗しました'
    hasPaymentMethod.value = false
  }
  
  // ユーザー情報の取得と設定
  const user = store.state.auth.user
  if (user) {
    formState.email = user.email
    formState.selectedPlan = store.getters['auth/currentSubscription'].planId
  } else {
    formState.selectedPlan = 'free'
  }

  if (currentPlan.value) {
    // ビジネスプランの場合は現在のアカウント数、それ以外は1をセット
    const initialAccountCount = currentPlan.value.planId === 'business' 
      ? currentPlan.value.currentAccountCount 
      : 1
    formState.accountCount = initialAccountCount
    accountUpdateForm.newAccountCount = initialAccountCount
  }

  await fetchPaymentMethods()
  
  // 支払い方法更新用のStripe Elements初期化
  if (showPaymentMethodForm.value) {
    updateCardElement.value = elements.create('card')
    updateCardElement.value.mount('#card-element-update')
    updateCardElement.value.on('change', function(event) {
      if (event.error) {
        paymentMethodError.value = event.error.message
      } else {
        paymentMethodError.value = ''
      }
    })
  }
})

onUnmounted(() => {
  if (card.value) {
    card.value.destroy()
  }
  if (updateCardElement.value) {
    updateCardElement.value.destroy()
  }
})
</script>

<style scoped>
.v-list-item--density-compact.v-list-item--one-line {
  min-height: auto;
}

.current-plan {
  border: 2px solid #1867c0;
}

.plan-card {
  height: 100%;
  transition: all 0.3s ease;
  position: relative;
}

.selected-plan {
  border: 2px solid currentColor;
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