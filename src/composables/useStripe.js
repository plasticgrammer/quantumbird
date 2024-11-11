import { ref, reactive } from 'vue'
import { loadStripe } from '@stripe/stripe-js'

export function useStripe() {
  const stripe = ref(null)
  const elements = ref(null)
  const cards = reactive({})

  const initializeStripe = async () => {
    try {
      const stripeKey = process.env.VUE_APP_STRIPE_PUBLISHABLE_KEY
      if (!stripeKey) {
        throw new Error('Stripe public key is not set')
      }

      // すでに初期化済みの場合は既存のインスタンスを返す
      if (stripe.value && elements.value) {
        return { stripe: stripe.value, elements: elements.value }
      }

      stripe.value = await loadStripe(stripeKey)
      elements.value = stripe.value.elements({
        locale: 'ja'
      })

      // 初期化完了を確実にするため少し待機
      await new Promise(resolve => setTimeout(resolve, 100))

      return { stripe: stripe.value, elements: elements.value }
    } catch (error) {
      console.error('Stripe initialization error:', error)
      throw error
    }
  }

  const createCardElement = async (elementId) => {
    if (!elements.value) {
      throw new Error('Stripe Elements has not been initialized')
    }

    try {
      // 既存のカード要素を破棄
      if (cards[elementId]) {
        cards[elementId].destroy()
        delete cards[elementId]
      }

      // DOMの準備を待機
      await new Promise(resolve => setTimeout(resolve, 100))

      const mountPoint = document.getElementById(elementId)
      if (!mountPoint) {
        throw new Error(`Mount point #${elementId} not found`)
      }

      // カード要素の作成
      cards[elementId] = elements.value.create('card', {
        style: {
          base: {
            fontSize: '16px',
            color: '#32325d',
            fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
            '::placeholder': {
              color: '#aab7c4'
            }
          },
          invalid: {
            color: '#fa755a',
            iconColor: '#fa755a'
          }
        },
        hidePostalCode: true
      })

      // マウント前に少し待機
      await new Promise(resolve => setTimeout(resolve, 100))

      // カード要素のマウント
      cards[elementId].mount(`#${elementId}`)
      return cards[elementId]
    } catch (error) {
      console.error('Card element creation error:', error)
      throw error
    }
  }

  const createToken = async (elementId, data) => {
    if (!stripe.value || !cards[elementId]) {
      throw new Error('Stripe has not been initialized')
    }

    return stripe.value.createToken(cards[elementId], data)
  }

  const destroyCardElement = (elementId) => {
    if (cards[elementId]) {
      cards[elementId].destroy()
      delete cards[elementId]
    }
  }

  return {
    stripe,
    elements,
    cards,
    initializeStripe,
    createCardElement,
    createToken,
    destroyCardElement
  }
}