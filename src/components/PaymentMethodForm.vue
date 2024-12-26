<template>
  <v-form ref="formRef" @submit.prevent="handleSubmit">
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

    <!-- スロット処理の改善 -->
    <div v-if="showSubmitButton">
      <slot name="submit-button">
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
          支払い方法を更新
        </v-btn>
      </slot>
    </div>
  </v-form>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import { useStripe } from '@/composables/useStripe'

const props = defineProps({
  elementId: {
    type: String,
    required: true
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

const validationRules = reactive({
  cardName: [
    v => !!v || 'カード名義は必須です'
  ]
})

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

// 外部からアクセスできるようにdefineExpose
defineExpose({
  submit
})

const handleSubmit = async () => {
  const result = await submit()
  if (result) {
    emit('submit', { token: result.token })
  }
}

onMounted(async () => {
  try {
    await nextTick()
    const { stripe, elements } = await initializeStripe()
    if (!stripe || !elements) {
      throw new Error('Stripe initialization failed')
    }

    // カード要素の初期化を確実に行う
    const card = await createCardElement(props.elementId)
    if (!card) {
      throw new Error('Card element creation failed')
    }

    card.on('change', (event) => {
      if (event.error) {
        error.value = event.error.message
        emit('error', error.value)
      } else {
        error.value = ''
      }
    })

    // フォームのリセット
    if (formRef.value) {
      formRef.value.reset()
    }

  } catch (err) {
    error.value = err.message || 'カード要素の初期化に失敗しました'
    emit('error', error.value)
  }
})

onUnmounted(() => {
  console.log('Cleaning up card element:', props.elementId)
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
