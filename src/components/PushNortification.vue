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
                :color="isSubscribed ? 'success' : 'grey'"
                class="mr-1"
                size="large"
              >
                {{ isSubscribed ? 'mdi-bell-outline' : 'mdi-bell-off-outline' }}
              </v-icon>
              {{ isSubscribed ? 'プッシュ通知: 有効' : 'プッシュ通知: 無効' }}
            </div>
          </template>
        </v-switch>
        <div v-else-if="notificationStatus === 'denied'">
          <span class="mx-2">プッシュ通知が拒否されています。</span>
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
import { ref, onMounted } from 'vue'
import { useStore } from 'vuex'
import { app } from '../config/firebase-config'
import { getMessaging, getToken } from 'firebase/messaging'
import { registerPushSubscription, removePushSubscription } from '../services/organizationService'

const store = useStore()
const isSubscribed = ref(false)
const notificationStatus = ref('default')
const isServiceWorkerReady = ref(false)
const hasError = ref(false)
const errorMessage = ref('')

const organizationId = store.getters['auth/organizationId']
const adminId = store.getters['auth/cognitoUserSub']

onMounted(async () => {
  await initializeServiceWorker()
  await checkNotificationStatus()
  await checkSubscription()
})

const canUseServiceWorker = () => {
  return 'serviceWorker' in navigator
}

const setError = (message) => {
  hasError.value = true
  errorMessage.value = message
}

const clearError = () => {
  hasError.value = false
  errorMessage.value = ''
}

const initializeServiceWorker = async () => {
  if (canUseServiceWorker()) {
    try {
      const registration = await navigator.serviceWorker.register('/firebase-messaging-sw.js', {
        scope: '/'
      })
      console.log('Service Worker registered successfully:', registration)
      
      // Service Workerの準備を待つ
      await waitForServiceWorkerReady()
      isServiceWorkerReady.value = true
      clearError()
    } catch (error) {
      console.error('Service Worker registration failed:', error)
      setError('Service Workerの登録に失敗しました。ページを再読み込みしてください。')
    }
  } else {
    setError('このブラウザはService Workerをサポートしていません。')
  }
}

const waitForServiceWorkerReady = () => {
  return new Promise((resolve) => {
    if (navigator.serviceWorker.controller) {
      resolve()
    } else {
      navigator.serviceWorker.addEventListener('controllerchange', () => {
        resolve()
      })
    }
  })
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
  if (!isServiceWorkerReady.value) {
    setError('Service Workerの準備ができていません。しばらく待ってから再試行してください。')
    return
  }
  
  try {
    const messaging = getMessaging(app)
    const fcmToken = await getToken(messaging)
    
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
    console.log('FCM token saved on server:', response.data)
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

const showInstructions = () => {
  alert(`ブラウザの通知設定を変更する方法:
    1. ブラウザの設定/環境設定を開きます。
    2. プライバシーとセキュリティ（または類似の項目）を探します。
    3. サイトの設定（または権限）を見つけます。
    4. 通知の設定を探し、このサイトの権限を「許可」に変更します。
    5. ページを再読み込みしてください。`)
}
</script>