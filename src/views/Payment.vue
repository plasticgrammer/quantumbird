<template>
  <v-container max-width="740px">
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
            cols="6"
            sm="6"
            md="5"
            class="pa-4"
          >
            <v-card
              :color="formState.selectedPlan === plan.id ? 'blue-accent-2' : ''"
              :class="[
                'plan-card',
                formState.selectedPlan === plan.id ? 'selected-plan' : ''
              ]"
              class="rounded-lg cursor-pointer"
              elevation="4"
              @click="formState.selectedPlan = plan.id"
            >
              <v-card-title class="text-center pt-6">
                <div class="text-h6 font-weight-bold">{{ plan.name }}</div>
              </v-card-title>

              <v-card-text>
                <div class="text-h4 font-weight-bold mb-4 text-center">
                  ¥{{ plan.price }}<span class="text-body-1">/月</span>
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
      <v-card-text v-if="formState.selectedPlan === 'price_pro'" class="mt-4">
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

          <!-- Stripe Elements マウントポイント -->
          <div class="mt-4">
            <label class="text-subtitle-1">カード情報</label>
            <div
              id="card-element"
              class="mt-2 pa-4 stripe-element"
              style="border: 1px solid #ccc; border-radius: 4px;"
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
import { ref, reactive, onMounted, onUnmounted } from 'vue'
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
    price: '0',
    display: 'フリープラン - 無料',
    features: ['基本機能が使用可能', '最大10名まで登録可能']
  },
  { 
    id: 'price_pro', 
    name: 'プロプラン',
    price: ' 1,000',
    display: 'プロプラン - ¥1,000/月',
    features: ['全機能が使用可能', 'メンバー数無制限']
  }
]

const formRef = ref(null)
const { initializeStripe, createToken, card } = useStripe()

const formState = reactive({
  email: '',
  cardName: '',
  selectedPlan: null
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
  errorMessage.value = ''
  if (formRef.value) {
    formRef.value.reset()
  }
}

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
        planId: formState.selectedPlan
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

  } catch (err) {
    errorMessage.value = err.message
  } finally {
    isLoading.value = false
  }
}

onMounted(async () => {
  await initializeStripe()
  // ユーザー情報の取得と設定
  const user = store.state.auth.user
  if (user) {
    formState.email = user.email
  }
  // デフォルトプランの設定
  formState.selectedPlan = plans[0].id
})

onUnmounted(() => {
  if (card.value) {
    card.value.destroy()
  }
})
</script>

<style scoped>
.plan-card {
  height: 100%;
  transition: all 0.3s ease;
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
</style>