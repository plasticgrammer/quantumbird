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

      // 既存のマウントポイントをクリア
      const mountPoint = document.getElementById('card-element')
      if (mountPoint) {
        mountPoint.innerHTML = ''
      }

      const stripeKey = process.env.VUE_APP_STRIPE_PUBLISHABLE_KEY
      if (!stripeKey) {
        throw new Error('Stripe public key is not set')
      }

      // betasとapiVersionの指定を削除
      stripe.value = await loadStripe(stripeKey)

      elements.value = stripe.value.elements({
        locale: 'ja' // 日本語化
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
        hidePostalCode: true // 郵便番号入力を非表示
      })

      // マウント前にエレメントが空であることを確認
      const cardElement = document.getElementById('card-element')
      if (cardElement) {
        cardElement.innerHTML = ''
        card.value.mount('#card-element')
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