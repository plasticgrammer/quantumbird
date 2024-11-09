<template>
  <v-container>
    <v-row dense class="pb-4">
      <v-col>
        <v-btn
          color="primary"
          variant="text"
          class="mb-4"
          @click="router.push({ name: 'AccountSetting' })"
        >
          <v-icon class="mr-2">mdi-arrow-left</v-icon>
          アカウント設定に戻る
        </v-btn>
      </v-col>
    </v-row>

    <v-card max-width="900" class="mx-auto">
      <v-card-title class="text-h5 font-weight-bold text-center pa-4">
        プラン選択
      </v-card-title>

      <!-- プラン選択カード -->
      <v-card-text>
        <v-row justify="center">
          <v-col
            v-for="plan in plans"
            :key="plan.id"
            cols="12"
            sm="6"
            md="4"
            class="pa-4"
          >
            <v-card
              :color="getCardColor(plan)"
              :class="[
                'plan-card',
                formState.selectedPlan === plan.id ? 'selected-plan' : '',
                currentPlan?.id === plan.id ? 'current-plan' : ''
              ]"
              class="rounded-lg cursor-pointer position-relative"
              elevation="4"
              @click="formState.selectedPlan = plan.id"
            >
              <!-- 現在のプランバッジ -->
              <v-chip
                v-if="currentPlan?.id === plan.id"
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
                  <template v-if="plan.id === 'price_business'">
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
                    :class="formState.selectedPlan === plan.id ? 'text-white' : ''"
                  >
                    <template #prepend>
                      <v-icon
                        :color="formState.selectedPlan === plan.id ? 'white' : 'primary'"
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
      <v-card-text v-show="formState.selectedPlan === 'price_pro' || formState.selectedPlan === 'price_business'" class="mt-4">
        <v-divider class="mb-6"></v-divider>
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
            v-if="formState.selectedPlan === 'price_business'"
            v-model="formState.accountCount"
            type="number"
            label="アカウント数"
            :rules="validationRules.accountCount"
            required
            :hint="`月額料金: ¥${plans.find(p => p.id === 'price_business').getPrice(formState.accountCount).toLocaleString()}/月`"
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
      </v-card-text>

      <!-- プラン変更セクション -->
      <v-card-text v-if="currentPlan && currentPlan.id === 'price_business'" class="mt-4">
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

const router = useRouter()
const store = useStore()
const emit = defineEmits(['payment-success']) // emitを定義

// プラン情報を定義
const plans = [
  { 
    id: 'price_free', 
    name: 'フリープラン',
    price: 0,
    features: ['基本機能が使用可能', '最大5名まで登録可能']
  },
  { 
    id: 'price_pro', 
    name: 'プロプラン',
    price: 1000,
    features: ['全機能が使用可能', 'メンバー数無制限']
  },
  {
    id: 'price_business',
    name: 'ビジネスプラン',
    price: 2000,
    pricePerAccount: 300, // 1アカウントあたり300円に設定
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
  if (currentPlan.value?.id === plan.id && formState.selectedPlan === plan.id) {
    return 'blue-darken-1' // 現在のプランかつ選択中
  }
  if (currentPlan.value?.id === plan.id) {
    return 'blue-lighten-4' // 現在のプラン
  }
  if (formState.selectedPlan === plan.id) {
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
  const plan = plans.find(p => p.id === subscription.planId) || plans[0]
  
  return {
    ...plan,
    currentAccountCount: subscription.accountCount
  }
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
    // カード情報のトークン化
    const { token, error } = await createToken({
      name: formState.cardName
    })

    if (error) {
      throw new Error(error.message)
    }

    // サブスクリプション作成APIの呼び出し
    const response = await fetch('/api/create-subscription', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        email: formState.email,
        token: token.id,
        planId: formState.selectedPlan,
        accountCount: formState.selectedPlan === 'price_business' ? formState.accountCount : 0
      })
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.message || '支払い処理に失敗しました')
    }

    // 成功時の処理
    showSuccessDialog.value = true
    resetForm()
    emit('payment-success')
    await store.dispatch('auth/fetchUser')

  } catch (err) {
    errorMessage.value = err.message
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
    const response = await fetch('/api/update-subscription', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        newAccountCount: accountUpdateForm.newAccountCount
      })
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.message || 'アカウント数の更新に失敗しました')
    }

    // 成功時の処理
    showSuccessDialog.value = true
    await store.dispatch('auth/fetchUser')
    // ストアのプラン情報を更新
    // await store.dispatch('subscription/updatePlan', await response.json())

  } catch (err) {
    errorMessage.value = err.message
  } finally {
    isUpdating.value = false
  }
}

onMounted(async () => {
  try {
    // DOMの準備を待ってからStripeを初期化
    await nextTick()
    await initializeStripe()
    
    // エラーハンドリングの追加
    if (card.value) {
      card.value.on('change', function(event) {
        if (event.error) {
          errorMessage.value = event.error.message
        } else {
          errorMessage.value = ''
        }
      })
    }
  } catch (error) {
    console.error('Failed to initialize Stripe:', error)
    errorMessage.value = 'カード情報フォームの初期化に失敗しました'
  }
  // ユーザー情報の取得と設定
  const user = store.state.auth.user
  if (user) {
    formState.email = user.email
    formState.selectedPlan = store.getters['auth/currentSubscription'].planId
  } else {
    formState.selectedPlan = 'price_free'
  }

  if (currentPlan.value) {
    formState.accountCount = currentPlan.value.currentAccountCount || 1
    accountUpdateForm.newAccountCount = currentPlan.value.currentAccountCount || 1
  }
})

onUnmounted(() => {
  if (card.value) {
    card.value.destroy()
  }
})
</script>

<style scoped>
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
</style>