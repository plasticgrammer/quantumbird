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
        
        <!-- プラン選択ボタン部分を変更 -->
        <v-row justify="center" class="mt-4">
          <v-col cols="12" sm="8" md="6">
            <v-btn
              v-if="formState.selectedPlan && formState.selectedPlan !== currentPlan.value?.planId"
              color="primary"
              block
              :loading="isLoading"
              :disabled="isLoading"
              @click="handlePlanSelection"
            >
              次へ
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>

      <!-- 支払い情報フォーム - 支払いステップの時のみ表示 -->
      <template v-else>
        <v-card-text class="px-6 py-4">
          <!-- 変更内容カード -->
          <v-card class="mb-4 pa-4" variant="outlined">
            <div class="text-subtitle-1 mb-2">変更内容</div>
            <div class="mb-2">
              現在のプラン: {{ currentPlan?.name || 'なし' }}
              <template v-if="currentPlan?.planId === 'business'">
                <div class="mt-1 ml-2">
                  現在の月額料金: ¥{{ currentPlan.getPrice(currentPlan.currentAccountCount).toLocaleString() }}
                </div>
              </template>
            </div>
            <v-divider class="my-2"></v-divider>
            <div>
              変更後のプラン: {{ plans.find(p => p.planId === formState.selectedPlan)?.name }}
              <template v-if="formState.selectedPlan === 'business'">
                <div class="mt-1 ml-2">
                  変更後の月額料金: ¥{{ plans.find(p => p.planId === 'business').getPrice(formState.accountCount).toLocaleString() }}
                </div>
              </template>
            </div>
          </v-card>
          <!-- ビジネスプラン用のアカウント数設定 -->
          <template v-if="formState.selectedPlan === 'business'">
            <v-card class="mb-4 pa-4" variant="outlined">
              <h3 class="text-h6 mb-4">アカウント数の設定</h3>
              <v-text-field
                v-model="formState.accountCount"
                type="number"
                label="アカウント数"
                :rules="validationRules.accountCount"
                :hint="`月額料金: ¥${plans.find(p => p.planId === 'business').getPrice(formState.accountCount).toLocaleString()}/月`"
                persistent-hint
                required
              ></v-text-field>
            </v-card>
          </template>

          <!-- 支払い方法セクション -->
          <template v-if="formState.selectedPlan === 'pro' || formState.selectedPlan === 'business'">
            <v-card class="mb-4 pa-4" variant="outlined">
              <h3 class="text-h6 mb-4">支払い方法</h3>
              
              <!-- 既存ユーザーの場合は現在の支払い方法を表示 -->
              <template v-if="!isNewCustomer">
                <div class="d-flex justify-space-between align-center">
                  <template v-if="!showPaymentMethodForm">
                    <div v-if="currentPaymentMethod" class="mt-2">
                      <div class="d-flex align-center">
                        <v-icon class="mr-2">mdi-credit-card</v-icon>
                        <span>**** **** **** {{ currentPaymentMethod.last4 }}</span>
                      </div>
                      <div class="text-caption">
                        有効期限: {{ String(currentPaymentMethod.expMonth).padStart(2, '0') }}/{{ String(currentPaymentMethod.expYear).slice(-2) }}
                      </div>
                    </div>
                    <v-btn
                      variant="text"
                      color="primary"
                      @click="showPaymentMethodForm = true"
                    >
                      変更する
                    </v-btn>
                  </template>
                </div>

                <!-- 支払い方法変更フォーム -->
                <PaymentMethodForm
                  v-if="showPaymentMethodForm"
                  element-id="card-element-update"
                  :loading="isUpdatingPaymentMethod"
                  @submit="handlePaymentMethodUpdate"
                  @error="paymentMethodError = $event"
                >
                  <template #submit-button>
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
                  </template>
                </PaymentMethodForm>
              </template>

              <!-- 新規ユーザーの場合は支払い方法入力フォーム -->
              <template v-else>
                <PaymentMethodForm
                  element-id="card-element"
                  submit-button-text="支払い方法を登録"
                  :loading="isLoading"
                  @submit="handlePaymentSubmit"
                  @error="errorMessage = $event"
                />
              </template>
            </v-card>
          </template>

          <!-- プラン変更確認ボタン -->
          <v-btn
            color="primary"
            block
            size="large"
            :loading="isLoading"
            :disabled="isLoading || (showPaymentMethodForm && isUpdatingPaymentMethod)"
            @click="handleSubmit"
          >
            {{ isLoading ? '処理中...' : formState.selectedPlan === 'free' ? 'プランを解約する' : 'プランを変更する' }}
          </v-btn>
        </v-card-text>

        <!-- 戻るボタン -->
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
import { createSubscription, getPaymentMethods, changePlan, updatePaymentMethod } from '../services/paymentService'
import PaymentMethodForm from '../components/PaymentMethodForm.vue'

const router = useRouter()
const store = useStore()
const { initializeStripe, cleanup, plans } = useStripe() // plansを追加

const emit = defineEmits(['payment-success']) // emitを定義

// Stripe要素の参照を追加
const updateCardElement = ref(null)

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

// 使用していない変数の削除

const formState = reactive({
  // emailプロパティを削除
  cardName: '',
  selectedPlan: null,
  accountCount: 1
})

const validationRules = {
  // emailの検証ルールを削除
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
const currentPaymentMethod = ref(null)

// computed プロパティの修正
const showPaymentMethodForm = ref(false)
const isUpdatingPaymentMethod = ref(false)
const paymentMethodError = ref('')

const hasPaymentMethod = ref(false)
const isNewCustomer = computed(() => !hasPaymentMethod.value)

// 現在のプラン情報を取得
const currentPlan = computed(() => {
  const subscription = store.getters['auth/currentSubscription']
  if (!subscription) return null
  
  const plan = plans.find(p => p.planId === subscription.planId) || plans[0]
  
  return {
    ...plan,
    subscriptionId: subscription.subscriptionId, // subscriptionIdを追加
    currentAccountCount: subscription.accountCount
  }
})

const resetForm = () => {
  formState.cardName = ''
  errorMessage.value = ''
}

// フォーム送信処理を修正
const handleSubmit = async () => {
  try {
    isLoading.value = true
    errorMessage.value = ''

    const selectedPlan = plans.find(p => p.planId === formState.selectedPlan)
    if (!selectedPlan) {
      throw new Error('無効なプランが選択されました')
    }

    // 現在のプランと同じ場合は処理しない
    if (formState.selectedPlan === currentPlan.value?.planId &&
        formState.accountCount === currentPlan.value?.currentAccountCount) {
      throw new Error('現在のプランと同じです')
    }

    // アカウント数のバリデーション（ビジネスプランの場合）
    if (formState.selectedPlan === 'business' &&
        (!formState.accountCount || formState.accountCount < 1)) {
      throw new Error('アカウント数は1以上を指定してください')
    }

    // subscriptionIdの存在確認
    // if (!currentPlan.value?.subscriptionId) {
    //   throw new Error('サブスクリプション情報が見つかりません')
    // }

    // Stripeのプラン変更を実行
    await changePlan({
      subscriptionId: currentPlan.value.subscriptionId,
      priceId: selectedPlan.priceId,
      accountCount: formState.selectedPlan === 'business' ? formState.accountCount : 0,
      signal: abortController.signal
    })

    // Cognitoの属性を更新
    await store.dispatch('auth/updateSubscriptionAttributes', {
      planId: selectedPlan.planId,
      accountCount: formState.selectedPlan === 'business' ? formState.accountCount : 0,
      subscriptionId: currentPlan.value.subscriptionId // 既存のsubscriptionIdを維持
    })

    showSuccessDialog.value = true
    await store.dispatch('auth/fetchUser')
    emit('payment-success')
  } catch (err) {
    if (err.name !== 'AbortError') {
      errorMessage.value = err.message || '処理に失敗しました'
      console.error('プラン変更エラー:', err)
    }
  } finally {
    isLoading.value = false
  }
}

const handlePaymentSubmit = async ({ token }) => {
  try {
    const selectedPlan = plans.find(p => p.planId === formState.selectedPlan)
    const userEmail = store.state.auth.user.email // 保持しているメールアドレスを使用
    
    // Stripeサブスクリプション作成
    const response = await createSubscription({
      email: userEmail, // 保持しているメールアドレスを使用
      token: token.id,
      priceId: selectedPlan.priceId,
      accountCount: formState.selectedPlan === 'business' ? formState.accountCount : 0
    })

    // レスポンスから subscriptionId を取得
    const { subscriptionId } = response.data

    // Cognitoの属性を更新（subscriptionId を含める）
    await store.dispatch('auth/updateSubscriptionAttributes', {
      planId: selectedPlan.planId,
      accountCount: formState.selectedPlan === 'business' ? formState.accountCount : 0,
      subscriptionId
    })

    showSuccessDialog.value = true
    resetForm()
    emit('payment-success')
    await store.dispatch('auth/fetchUser')
  } catch (err) {
    errorMessage.value = err.message || '処理に失敗しました'
  }
}

const handlePaymentMethodUpdate = async ({ token }) => {
  isUpdatingPaymentMethod.value = true
  paymentMethodError.value = ''

  try {
    // 支払い方法更新APIの呼び出し
    await updatePaymentMethod({
      token: token.id
    })

    // 現在のサブスクリプション情報でCognitoの属性を再同期
    await store.dispatch('auth/updateSubscriptionAttributes', {
      planId: currentPlan.value.planId,
      accountCount: currentPlan.value.currentAccountCount
    })

    await fetchPaymentMethods()
    showPaymentMethodForm.value = false

  } catch (err) {
    paymentMethodError.value = err.message || '支払い方法の更新に失敗しました'
  } finally {
    isUpdatingPaymentMethod.value = false
  }
}

const fetchPaymentMethods = async () => {
  const user = store.state.auth.user
  if (!user) return

  try {
    const response = await getPaymentMethods(user.email, { 
      signal: abortController.signal 
    })
    const methods = response?.data?.paymentMethods || []
    currentPaymentMethod.value = methods[0]
    hasPaymentMethod.value = methods.length > 0
  } catch (error) {
    if (!error.name === 'AbortError') {
      console.error('支払い方法の取得に失敗しました:', error)
    }
  }
}

const abortController = new AbortController()

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
      await fetchPaymentMethods()
    } else {
      formState.selectedPlan = 'free'
    }

    if (currentPlan.value) {
      const initialAccountCount = currentPlan.value.planId === 'business' 
        ? currentPlan.value.currentAccountCount 
        : 1
      formState.accountCount = initialAccountCount
    }
  } catch (error) {
    if (!error.name === 'AbortError') {
      console.error('初期化に失敗しました:', error)
      errorMessage.value = '初期化に失敗しました'
    }
    hasPaymentMethod.value = false
  }
})

onUnmounted(() => {
  abortController.abort()
  if (updateCardElement.value) {
    updateCardElement.value.destroy()
  }
  cleanup()
})

// ステップ管理用の状態を追加
const currentStep = ref('plan-selection') // 'plan-selection' または 'payment'

// プラン選択から支払いステップへの遷移
const handlePlanSelection = () => {
  //if (formState.selectedPlan && formState.selectedPlan !== currentPlan.value?.planId) {
  currentStep.value = 'payment'
  //}
}

// ステップのタイトルを取得する計算プロパティを追加
const getStepTitle = computed(() => {
  switch (currentStep.value) {
  case 'payment':
    return formState.selectedPlan === 'business' 
      ? 'アカウント数設定・支払い情報' 
      : 'プラン変更'
  default:
    return 'プラン選択'
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