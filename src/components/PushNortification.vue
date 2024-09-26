<template>
  <v-container class="pa-0">
    <v-row align="center" justify="start" no-gutters>
      <v-col cols="auto">
        <v-switch
          v-if="notificationStatus === 'default' || notificationStatus === 'granted'"
          v-model="isSubscribed"
          color="primary"
          hide-details
          inset
          :disabled="!isServiceWorkerReady"
          @click="togglePushNotification"
        >
          <template #prepend>
            <div v-if="notificationStatus === 'default' || notificationStatus === 'granted'">
              <v-icon
                :color="iconColor"
                class="mr-1"
                size="large"
              >
                {{ iconName }}
              </v-icon>
              {{ statusText }}
            </div>
          </template>
        </v-switch>
        <div v-else-if="notificationStatus === 'denied'">
          <span class="text-error mx-2">プッシュ通知が拒否されています。</span>
          <v-btn
            color="grey"
            small
            @click="showInstructions"
          >
            設定変更方法を表示
          </v-btn>
        </div>
      </v-col>
      <v-col v-if="hasError" cols="auto">
        <div class="v-input--error">
          <div class="v-messages">
            <div class="v-messages__message pl-4">
              {{ errorMessage }}
            </div>
          </div>
        </div>    
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, computed, watchEffect, onMounted, onUnmounted } from 'vue'
import { useStore } from 'vuex'
import { app } from '../config/firebase-config'
import { contextPath } from '../config/environment'
import { getMessaging, getToken } from 'firebase/messaging'
import { registerPushSubscription, removePushSubscription } from '../services/organizationService'

const store = useStore()
const isSubscribed = ref(false)
const notificationStatus = ref('default')
const isServiceWorkerReady = ref(false)
const hasError = ref(false)
const errorMessage = ref('')
const statusCheckInterval = ref(null)

const organizationId = store.getters['auth/organizationId']
const adminId = store.getters['auth/cognitoUserSub']

const iconName = computed(() => {
  if (!isServiceWorkerReady.value) return 'mdi-progress-clock'
  return isSubscribed.value ? 'mdi-bell-outline' : 'mdi-bell-off-outline'
})

const iconColor = computed(() => {
  if (!isServiceWorkerReady.value) return 'grey'
  return isSubscribed.value ? 'success' : 'grey'
})

const statusText = computed(() => {
  if (!isServiceWorkerReady.value) return 'Service Worker初期化中'
  return isSubscribed.value ? 'プッシュ通知: 有効' : 'プッシュ通知: 無効'
})

watchEffect(async () => {
  if (isServiceWorkerReady.value) {
    await checkNotificationStatus()
    await checkSubscription()
  }
})

onMounted(async () => {
  await initializeServiceWorker()
  statusCheckInterval.value = setInterval(checkServiceWorkerStatus, 5000)
})

onUnmounted(() => {
  if (statusCheckInterval.value) {
    clearInterval(statusCheckInterval.value)
  }
})

const initializeServiceWorker = async () => {
  if ('serviceWorker' in navigator) {
    try {
      console.log('Registering Service Worker...')
      const swPath = `${contextPath}firebase-messaging-sw.js`
      const registration = await navigator.serviceWorker.register(swPath, {
        scope: contextPath
      })
      console.log('Service Worker registered successfully:', registration)
      
      console.log('Waiting for registration to become ready...')
      await registration.ready
      console.log('Registration is ready')
      
      console.log('Waiting for Service Worker to become ready...')
      await Promise.race([
        waitForServiceWorkerReady(),
        new Promise((_, reject) => setTimeout(() => reject(new Error('Service Worker ready timeout')), 15000))
      ])
      console.log('Service Worker is ready')
      
      isServiceWorkerReady.value = true
      clearError()
    } catch (error) {
      console.error('Service Worker initialization failed:', error)
      setError(`Service Workerの初期化に失敗しました: ${error.message}`)
      isServiceWorkerReady.value = false
    }
  } else {
    console.warn('This browser does not support Service Workers')
    setError('このブラウザはService Workerをサポートしていません。')
    isServiceWorkerReady.value = false
  }
}

const waitForServiceWorkerReady = () => {
  return new Promise((resolve) => {
    const checkController = () => {
      if (navigator.serviceWorker.controller) {
        console.log('Service Worker is now controlling the page')
        resolve()
      } else {
        console.log('Service Worker is not yet controlling the page, waiting...')
        setTimeout(checkController, 1000)
      }
    }

    navigator.serviceWorker.ready.then((registration) => {
      console.log('Service Worker is ready:', registration)
      checkController()
    })

    navigator.serviceWorker.addEventListener('controllerchange', () => {
      console.log('Service Worker controller changed')
      checkController()
    })
  })
}

const checkServiceWorkerStatus = () => {
  if (navigator.serviceWorker.controller) {
    console.log('Service Worker controller:', navigator.serviceWorker.controller.state)
    navigator.serviceWorker.getRegistrations().then(registrations => {
      console.log('Service Worker registrations:', registrations)
      if (registrations.length > 0) {
        console.log('Service Worker is registered. Stopping periodic checks.')
        clearInterval(statusCheckInterval.value)
        statusCheckInterval.value = null
      }
    })
  } else {
    console.log('No Service Worker controller')
  }
}

const checkNotificationStatus = async () => {
  if ('Notification' in window) {
    notificationStatus.value = Notification.permission
  }
}

const checkSubscription = async () => {
  const token = await getStoredToken()
  isSubscribed.value = !!token
}

const togglePushNotification = async () => {
  if (!isServiceWorkerReady.value) {
    setError('Service Workerの準備ができていません。しばらく待ってから再試行してください。')
    return
  }
  
  clearError()
  if (notificationStatus.value === 'default') {
    const permission = await Notification.requestPermission()
    notificationStatus.value = permission
    if (permission === 'granted') {
      await subscribeToPush()
    } else {
      isSubscribed.value = false
    }
  } else if (notificationStatus.value === 'granted') {
    if (isSubscribed.value) {
      await unsubscribeFromPush()
    } else {
      await subscribeToPush()
    }
  }
  await checkSubscription()
}

const subscribeToPush = async () => {
  try {
    const messaging = getMessaging(app)
    const registration = await navigator.serviceWorker.getRegistration(contextPath)
    const fcmToken = await getToken(messaging, { 
      serviceWorkerRegistration: registration 
    })
    
    if (fcmToken) {
      await saveSubscription(fcmToken)
      isSubscribed.value = true
      console.log('Subscribed to push notifications')
    } else {
      setError('FCMトークンの取得に失敗しました。')
    }
  } catch (error) {
    console.error('Failed to subscribe to push notifications:', error)
    setError(`プッシュ通知の購読に失敗しました: ${error.message}`)
  }
}

const unsubscribeFromPush = async () => {
  const token = await getStoredToken()
  if (token) {
    try {
      await deleteSubscription(token)
      isSubscribed.value = false
      console.log('Unsubscribed from push notifications')
    } catch (error) {
      console.error('Failed to unsubscribe from push notifications:', error)
      setError('プッシュ通知の購読解除に失敗しました。')
    }
  }
}

const saveSubscription = async (fcmToken) => {
  try {
    const response = await registerPushSubscription(fcmToken, organizationId, adminId)
    await storeToken(fcmToken)
    console.log('FCM token saved on server:', response.endpointArn)
  } catch (error) {
    console.error('Failed to save FCM token on server:', error)
    throw error
  }
}

const deleteSubscription = async () => {
  try {
    await removePushSubscription(organizationId, adminId)
    await removeStoredToken()
  } catch (error) {
    console.error('Failed to delete subscription on server:', error)
    throw error
  }
}

const storeToken = async (fcmToken) => {
  localStorage.setItem('fcmToken', fcmToken)
}

const getStoredToken = async () => {
  return localStorage.getItem('fcmToken')
}

const removeStoredToken = async () => {
  localStorage.removeItem('fcmToken')
}

const setError = (message) => {
  hasError.value = true
  errorMessage.value = message
}

const clearError = () => {
  hasError.value = false
  errorMessage.value = ''
}

const showInstructions = () => {
  alert(`ブラウザの通知設定を変更する方法:
    1. ブラウザの設定/環境設定を開きます。
    2. プライバシーとセキュリティ（または類似の項目）を探します。
    3. サイトの設定（または権限）を見つけます。
    4. 通知の設定を探し、このサイトの権限を「許可」に変更します。
    5. ページを再読み込みしてください。`)
}
</script>