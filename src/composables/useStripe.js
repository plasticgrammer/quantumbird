import { ref } from 'vue'
import { loadStripe } from '@stripe/stripe-js'

export function useStripe() {
  const stripe = ref(null)
  const card = ref(null)
  const elements = ref(null)

  const initializeStripe = async () => {
    try {
      // すでにカードエレメントが存在する場合は破棄
      if (card.value) {
        card.value.destroy()
      }

      const stripeKey = process.env.VUE_APP_STRIPE_PUBLISHABLE_KEY
      if (!stripeKey) {
        throw new Error('Stripe public key is not set')
      }

      // Stripeの初期化
      stripe.value = await loadStripe(stripeKey)

      // 要素の初期化を待機
      await new Promise(resolve => setTimeout(resolve, 100))

      elements.value = stripe.value.elements({
        locale: 'ja'
      })

      const style = {
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
      }

      card.value = elements.value.create('card', {
        style,
        hidePostalCode: true
      })

      // DOMの準備を待機
      await new Promise(resolve => setTimeout(resolve, 100))

      const cardElement = document.getElementById('card-element')
      if (cardElement) {
        card.value.mount('#card-element')
      } else {
        throw new Error('Card element mount point not found')
      }

      return card.value
    } catch (error) {
      console.error('Stripe initialization error:', error)
      throw error
    }
  }

  const createToken = async (data) => {
    if (!stripe.value || !card.value) {
      throw new Error('Stripe has not been initialized')
    }

    return stripe.value.createToken(card.value, data)
  }

  return {
    stripe,
    card,
    elements,
    initializeStripe,
    createToken
  }
}