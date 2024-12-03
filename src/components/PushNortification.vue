<template>
  <v-container class="pa-0">
    <v-row align="center" justify="start" no-gutters>
      <v-col cols="11">
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
            <v-icon
              :color="iconColor"
              class="mr-1"
              size="large"
            >
              {{ iconName }}
            </v-icon>
            {{ statusText }}
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
      
      <v-col cols="11" class="mt-2">
        <div class="text-body-2 text-grey pl-3">
          <div class="d-flex align-center mb-1">
            <v-icon size="small" class="mr-2" :color="isSubscribed ? 'success' : 'grey'">
              {{ isSubscribed ? 'mdi-check-circle' : 'mdi-circle-outline' }}
            </v-icon>
            <span>通知設定: {{ isSubscribed ? '登録済み' : '未登録' }}</span>
          </div>
          <div class="d-flex align-center mb-1">
            <v-icon size="small" class="mr-2" :color="isServiceWorkerReady ? 'success' : 'grey'">
              {{ isServiceWorkerReady ? 'mdi-check-circle' : 'mdi-progress-clock' }}
            </v-icon>
            <span>システム準備状況: {{ isServiceWorkerReady ? '完了' : '準備中' }}</span>
          </div>
          <div class="d-flex align-center">
            <v-icon size="small" class="mr-2" :color="notificationStatus === 'granted' ? 'success' : 'grey'">
              {{ notificationStatus === 'granted' ? 'mdi-check-circle' : 'mdi-alert-circle' }}
            </v-icon>
            <span>ブラウザの許可: {{ 
              notificationStatus === 'granted' ? '許可済み' :
              notificationStatus === 'denied' ? '拒否' :
              '未設定'
            }}</span>
          </div>
        </div>
      </v-col>

      <v-col v-if="hasError" cols="11">
        <div class="v-input--error">
          <div class="v-messages">
            <div class="v-messages__message pl-4">
              {{ errorMessage }}
            </div>
          </div>
        </div>
      </v-col>
      <v-col v-if="hasError" cols="1" class="d-flex justify-end">
        <v-btn
          v-if="isServiceWorkerReady" 
          icon="mdi-reload"
          color="error"
          density="comfortable"
          @click="resetServiceWorker"
        >
        </v-btn>
      </v-col>
      <v-col v-if="!isOnline" cols="auto">
        <v-chip color="warning" small>
          オフライン
        </v-chip>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useStore } from 'vuex'
import { app } from '../config/firebase-config'
import { contextPath } from '../config/environment'
import { getMessaging, getToken } from 'firebase/messaging'
import { registerPushSubscription, removePushSubscription, getPushSubscription } from '../services/organizationService'

const store = useStore()
const isSubscribed = ref(false)
const notificationStatus = ref('default')
const isServiceWorkerReady = ref(false)
const hasError = ref(false)
const errorMessage = ref('')
const isOnline = ref(navigator.onLine)
const statusCheckInterval = ref(null)

const organizationId = store.getters['auth/organizationId']
const adminId = store.getters['auth/cognitoUserSub']

const iconName = computed(() => {
  return isServiceWorkerReady.value ? (isSubscribed.value ? 'mdi-bell-outline' : 'mdi-bell-off-outline') : 'mdi-progress-clock'
})

const iconColor = computed(() => {
  return isServiceWorkerReady.value ? (isSubscribed.value ? 'success' : 'grey') : 'grey'
})

const statusText = computed(() => {
  return isServiceWorkerReady.value ? (isSubscribed.value ? 'プッシュ通知: 有効' : 'プッシュ通知: 無効') : 'Service Worker初期化中'
})

watch(isServiceWorkerReady, async (newValue) => {
  console.log('isServiceWorkerReady changed:', newValue)
  if (newValue) {
    await checkNotificationStatus()
    await checkSubscription()
    await nextTick()
  }
})

onMounted(() => {
  window.addEventListener('online', updateOnlineStatus)
  window.addEventListener('offline', updateOnlineStatus)

  nextTick(async () => {
    try {
      await initializeServiceWorker()
      console.log('Service Worker initialization completed')
      console.log('Final isServiceWorkerReady value:', isServiceWorkerReady.value)
    } catch (error) {
      console.error('Failed to initialize Service Worker:', error)
    }
  })
})

onUnmounted(() => {
  window.removeEventListener('online', updateOnlineStatus)
  window.removeEventListener('offline', updateOnlineStatus)
  if (statusCheckInterval.value) {
    clearInterval(statusCheckInterval.value)
  }
})

const updateOnlineStatus = () => {
  isOnline.value = navigator.onLine
  console.log('Online status updated:', isOnline.value)
}

const initializeServiceWorker = async () => {
  if ('serviceWorker' in navigator) {
    try {
      console.log('Registering Service Worker...')
      const swPath = `${contextPath}firebase-messaging-sw.js`
      const registration = await navigator.serviceWorker.register(swPath, {
        scope: contextPath
      })
      console.log('Service Worker registered successfully:', registration)

      await waitForServiceWorkerReady(registration)
      
      isServiceWorkerReady.value = true
      console.log('isServiceWorkerReady set to true')
      clearError()
      
      await nextTick()
      console.log('After nextTick, isServiceWorkerReady:', isServiceWorkerReady.value)
      
    } catch (error) {
      console.error('Service Worker initialization failed:', error)
      setError(`Service Workerの初期化に失敗しました: ${error.message}`)
      isServiceWorkerReady.value = false
      await nextTick()
      showReloadPrompt()
    }
  } else {
    console.warn('This browser does not support Service Workers')
    setError('このブラウザはService Workerをサポートしていません。')
    isServiceWorkerReady.value = false
  }
}

const showReloadPrompt = () => {
  // ユーザーに一度だけ再読み込みを確認する
  if (!window.hasShownReloadPrompt) {
    window.hasShownReloadPrompt = true
    if (confirm('Service Workerの初期化に失敗しました。ページを再読み込みしますか？')) {
      window.location.reload()
    }
  }
}

const waitForServiceWorkerReady = async (registration) => {
  return new Promise((resolve, reject) => {
    const timeout = setTimeout(() => {
      reject(new Error('Service Worker ready timeout'))
    }, 30000)

    const checkState = () => {
      if (registration.active && navigator.serviceWorker.controller) {
        clearTimeout(timeout)
        resolve()
      } else {
        setTimeout(checkState, 1000)
      }
    }

    if (registration.active && navigator.serviceWorker.controller) {
      clearTimeout(timeout)
      resolve()
    } else {
      registration.addEventListener('updatefound', checkState)
      navigator.serviceWorker.addEventListener('controllerchange', checkState)
      checkState()
    }
  })
}

const checkNotificationStatus = async () => {
  if ('Notification' in window) {
    notificationStatus.value = Notification.permission
    console.log('Notification status checked:', notificationStatus.value)
  }
}

const checkSubscription = async () => {
  const endpoint = await getStoredEndpointArn()
  if (endpoint) {
    try {
      const serverEndpoint = await getPushSubscription(organizationId, adminId)
      isSubscribed.value = endpoint === serverEndpoint
      console.log('Subscription checked, isSubscribed:', isSubscribed.value)
    } catch (error) {
      console.error('Failed to check subscription on server:', error)
      setError('サーバーでの購読確認に失敗しました。')
    }
  } else {
    isSubscribed.value = false
  }
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
  const endpoint = await getStoredEndpointArn()
  if (endpoint) {
    try {
      await deleteSubscription()
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
    await storeEndpointArn(response.endpointArn)
    console.log('FCM token saved on server:', response.endpointArn)
  } catch (error) {
    console.error('Failed to save FCM token on server:', error)
    throw error
  }
}

const deleteSubscription = async () => {
  try {
    await removePushSubscription(organizationId, adminId)
    await removeStoredEndpointArn()
  } catch (error) {
    console.error('Failed to delete subscription on server:', error)
    throw error
  }
}

const storeEndpointArn = async (endpointArn) => {
  localStorage.setItem('endpointArn', endpointArn)
}

const getStoredEndpointArn = async () => {
  return localStorage.getItem('endpointArn')
}

const removeStoredEndpointArn = async () => {
  localStorage.removeItem('endpointArn')
}

const setError = (message) => {
  hasError.value = true
  errorMessage.value = message
  console.error('Error set:', message)
}

const clearError = () => {
  hasError.value = false
  errorMessage.value = ''
  console.log('Error cleared')
}

const showInstructions = () => {
  alert(`ブラウザの通知設定を変更する方法:
    1. ブラウザの設定/環境設定を開きます。
    2. プライバシーとセキュリティ（または類似の項目）を探します。
    3. サイトの設定（または権限）を見つけます。
    4. 通知の設定を探し、このサイトの権限を「許可」に変更します。
    5. ページを再読み込みしてください。`)
}

const clearServiceWorkerCache = async () => {
  if ('caches' in window) {
    const cacheNames = await caches.keys()
    await Promise.all(cacheNames.map(cacheName => caches.delete(cacheName)))
    console.log('Service Worker caches cleared')
  }
}

const resetServiceWorker = async () => {
  if ('serviceWorker' in navigator) {
    const registrations = await navigator.serviceWorker.getRegistrations()
    for (let registration of registrations) {
      await registration.unregister()
    }
    await clearServiceWorkerCache()
    console.log('Service Worker reset complete')
    window.location.reload()
  }
}
</script>