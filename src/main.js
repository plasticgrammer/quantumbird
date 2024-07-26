import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import vuetify from './plugins/vuetify'
import { loadFonts } from './plugins/webfontloader'
import { Amplify } from 'aws-amplify'
import amplifyConfig from './config/amplify-config'
import './assets/global.css'

// Amplify の設定
try {
  Amplify.configure(amplifyConfig, { ssr: true })
  console.log('Amplify configured successfully')
} catch (error) {
  console.error('Failed to configure Amplify:', error)
}

// フォントの読み込み
loadFonts()

// Vue アプリケーションの作成と設定
const app = createApp(App)

app.use(router)
app.use(store)
app.use(vuetify)

// グローバルエラーハンドラー
app.config.errorHandler = (err, vm, info) => {
  console.error('Unhandled error:', err, info)
  // ここにエラー報告ロジックを追加することができます
}

// アプリケーションのマウント
app.mount('#app')
