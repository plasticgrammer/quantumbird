<template>
  <v-form ref="formRef">
    <!-- カード所有者名 -->
    <v-text-field
      v-model="formData.cardName"
      label="カード名義"
      :rules="validationRules.cardName"
      required
    ></v-text-field>

    <!-- Stripe Elements マウントポイント -->
    <div class="mt-4">
      <label class="text-subtitle-1">カード情報</label>
      <div
        :id="elementId"
        class="mt-2 pa-4 stripe-element"
        style="min-height: 40px"
      ></div>
      <div
        v-if="error"
        class="error--text mt-2"
      >
        {{ error }}
      </div>
    </div>

    <!-- 送信ボタン - showSubmitButtonがtrueの場合のみ表示 -->
    <slot v-if="showSubmitButton" name="submit-button">
      <v-btn
        type="submit"
        color="primary"
        class="mt-6"
        block
        size="large"
        :loading="loading"
        :disabled="loading"
        @click.prevent="handleSubmit"
      >
        {{ loading ? '処理中...' : submitButtonText }}
      </v-btn>
    </slot>
  </v-form>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useStripe } from '../composables/useStripe'

const props = defineProps({
  elementId: {
    type: String,
    required: true
  },
  submitButtonText: {
    type: String,
    default: '支払い方法を更新'
  },
  loading: {
    type: Boolean,
    default: false
  },
  showSubmitButton: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['submit', 'error'])

const formRef = ref(null)
const error = ref('')
const { initializeStripe, createCardElement, createToken, destroyCardElement } = useStripe()

const formData = reactive({
  cardName: ''
})

// Define validationRules as a reactive const instead of a local variable
/* eslint-disable-next-line no-unused-vars */
const validationRules = reactive({
  cardName: [
    v => !!v || 'カード名義は必須です'
  ]
})

// submitメソッドを外部から呼び出せるように定義
const submit = async () => {
  const form = formRef.value
  if (!form) return null
  
  const { valid } = await form.validate()
  if (!valid) return null

  error.value = ''

  try {
    const { token, error: tokenError } = await createToken(props.elementId, {
      name: formData.cardName
    })

    if (tokenError) throw new Error(tokenError.message)
    return { token }
    
  } catch (err) {
    error.value = err.message || '処理に失敗しました'
    emit('error', error.value)
    return null
  }
}

// フォーム送信ハンドラ - ボタンクリック時
const handleSubmit = async () => {
  const result = await submit()
  if (result) {
    emit('submit', { token: result.token })
  }
}

// 外部からアクセスできるようにdefineExpose
defineExpose({
  submit
})

onMounted(async () => {
  try {
    const { stripe, elements } = await initializeStripe()
    if (!stripe || !elements) {
      throw new Error('Stripe initialization failed')
    }

    const card = await createCardElement(props.elementId)
    if (!card) {
      throw new Error('Card element creation failed')
    }

    card.on('change', (event) => {
      if (event.error) {
        error.value = event.error.message
      } else {
        error.value = ''
      }
    })
  } catch (err) {
    error.value = err.message || 'カード要素の初期化に失敗しました'
  }
})

onUnmounted(() => {
  destroyCardElement(props.elementId)
})
</script>

<style scoped>
.stripe-element {
  min-height: 40px;
  background-color: white;
}

.stripe-element:empty {
  background-color: white;
}
</style>
