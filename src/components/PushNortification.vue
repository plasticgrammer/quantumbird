<template>
  <v-container class="pa-0">
    <v-row align="center" justify="start" no-gutters>
      <v-col cols="auto" class="ml-2 mr-4">
        <div v-if="notificationStatus === 'default' || notificationStatus === 'granted'">
          <v-icon
            :color="isSubscribed ? 'success' : 'grey'"
            class="mr-1"
            size="large"
          >
            {{ isSubscribed ? 'mdi-bell-outline' : 'mdi-bell-off-outline' }}
          </v-icon>
          {{ isSubscribed ? 'プッシュ通知: ON' : 'プッシュ通知: OFF' }}
        </div>
        <div v-else-if="notificationStatus === 'denied'">
          プッシュ通知が拒否されています。
        </div>
      </v-col>
      <v-col cols="auto">
        <v-switch
          v-if="notificationStatus === 'default' || notificationStatus === 'granted'"
          v-model="isSubscribed"
          color="primary"
          hide-details
          inset
          :disabled="!isServiceWorkerReady"
          @click="togglePushNotification"
        ></v-switch>
        <v-btn
          v-else-if="notificationStatus === 'denied'"
          color="secondary"
          small
          @click="showInstructions"
        >
          設定変更方法を表示
        </v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted, inject } from 'vue'
import { useStore } from 'vuex'
import { app } from '../config/firebase-config'
import { getMessaging, getToken } from 'firebase/messaging'
import { registerPushSubscription, removePushSubscription } from '../services/organizationService'

const store = useStore()
const isSubscribed = ref(false)
const notificationStatus = ref('default')
const isServiceWorkerReady = ref(false)
const showError = inject('showError')

const organizationId = store.getters['auth/organizationId']
const adminId = store.getters['auth/cognitoUserSub']

onMounted(async () => {
  await initializeServiceWorker()
  await checkNotificationStatus()
  await checkSubscription()
})

const isIOSSafari = async () => {
  const ua = window.navigator.userAgent
  const iOS = !!ua.match(/iPad/i) || !!ua.match(/iPhone/i)
  const webkit = !!ua.match(/WebKit/i)
  const iOSSafari = iOS && webkit && !ua.match(/CriOS/i) && !ua.match(/FxiOS/i)
  
  // iOS 13以降のiPadはユーザーエージェントがMacのように見えるため、追加チェック
  const isIPadOS = navigator.maxTouchPoints && navigator.maxTouchPoints > 2 && /MacIntel/.test(navigator.platform)
  
  return iOSSafari || isIPadOS
}

const canUseServiceWorker = () => {
  return 'serviceWorker' in navigator && 
         navigator.serviceWorker.controller !== null
}

const initializeServiceWorker = async () => {
  if (canUseServiceWorker() && !isIOSSafari()) {
    try {
      const registration = await navigator.serviceWorker.register('/firebase-messaging-sw.js', {
        scope: '/'
      })
      console.log('Service Worker registered successfully:', registration)
      
      // Service Workerがアクティブになるのを待つ
      await navigator.serviceWorker.ready
      isServiceWorkerReady.value = true
    } catch (error) {
      console.error('Service Worker registration failed:', error)
      showError('Service Workerの登録に失敗しました。ページを再読み込みしてください。')
    }
  } else if (isIOSSafari()) {
    console.log('iOS SafariではService Workerの一部機能が制限されています。')
  } else {
    showError('このブラウザはService Workerをサポートしていません。')
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
    showError('Service Workerの準備ができていません。しばらく待ってから再試行してください。')
    return
  }
  
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
    const fcmToken = await getToken(messaging)
    
    if (fcmToken) {
      await saveSubscription(fcmToken)
      isSubscribed.value = true
      console.log('Subscribed to push notifications')
    } else {
      showError('FCMトークンの取得に失敗しました。')
    }
  } catch (error) {
    console.error('Failed to subscribe to push notifications:', error)
    showError('プッシュ通知の購読に失敗しました。Service Workerが正しく動作していることを確認してください。')
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
      showError('プッシュ通知の購読解除に失敗しました。')
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
  alert(`
    ブラウザの通知設定を変更する方法:
    1. ブラウザの設定/環境設定を開きます。
    2. プライバシーとセキュリティ（または類似の項目）を探します。
    3. サイトの設定（または権限）を見つけます。
    4. 通知の設定を探し、このサイトの権限を「許可」に変更します。
    5. ページを再読み込みしてください。
  `)
}
</script>