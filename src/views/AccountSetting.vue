<template>
  <v-container>
    <v-row dense class="pb-4">
      <v-col>
        <h3>
          <v-icon size="large" class="mr-1">mdi-cog-outline</v-icon>
          アカウント設定
        </h3>
      </v-col>
    </v-row>

    <v-row>
      <v-col>
        <v-card>
          <v-card-title>アカウント設定</v-card-title>
          <v-card-text>
            <v-form @submit.prevent="updateSettings">
              <v-text-field
                v-model="email"
                label="メールアドレス"
                readonly
              ></v-text-field>
              <!-- 他の編集可能なフィールドをここに追加 -->
              <v-btn color="primary" type="submit">設定を保存</v-btn>
            </v-form>
          </v-card-text>
        </v-card>

        <v-card class="mt-4">
          <v-card-title>データ管理</v-card-title>
          <v-card-text>
            <v-btn color="info" :loading="isExporting" @click="exportData">
              データをエクスポート
            </v-btn>
            <p v-if="exportStatus" class="mt-2">{{ exportStatus }}</p>
          </v-card-text>
        </v-card>

        <v-card class="mt-4">
          <v-card-title class="error--text">危険ゾーン</v-card-title>
          <v-card-text>
            <p class="mb-4">一度アカウントを削除すると、二度と元に戻せません。十分ご注意ください。</p>
            <v-btn color="error" @click="showDeleteConfirmation = true">
              アカウントを削除
            </v-btn>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 削除確認ダイアログ -->
    <v-dialog v-model="showDeleteConfirmation" max-width="400px">
      <v-card>
        <v-card-title>アカウント削除の確認</v-card-title>
        <v-card-text>
          <p class="mb-4">
            本当にアカウントを削除しますか？<br>この操作は取り消せません。
          </p>
          <v-text-field
            v-model="confirmationText"
            label="確認のため 'DELETE' と入力してください"
            hide-details
          ></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" text @click="showDeleteConfirmation = false">キャンセル</v-btn>
          <v-btn
            color="error"
            :disabled="confirmationText !== 'DELETE'"
            @click="deleteAccount"
          >
            削除する
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

const store = useStore()
const router = useRouter()

const email = ref('')
const showDeleteConfirmation = ref(false)
const confirmationText = ref('')
const isExporting = ref(false)
const exportStatus = ref('')

const user = computed(() => store.state.auth.user)

onMounted(() => {
  email.value = user.value.email
  // 他の設定フィールドの初期化
})

const updateSettings = async () => {
  try {
    // 設定の更新処理
    await store.dispatch('auth/updateUserSettings', { /* 更新するフィールド */ })
    store.dispatch('showNotification', {
      message: '設定が更新されました',
      type: 'success'
    })
  } catch (error) {
    store.dispatch('showNotification', {
      message: '設定の更新に失敗しました',
      type: 'error'
    })
  }
}

const deleteAccount = async () => {
  try {
    await store.dispatch('auth/deleteUserAccount')
    store.dispatch('showNotification', {
      message: 'アカウントが削除されました',
      type: 'success'
    })
    router.push('/login') // ログインページにリダイレクト
  } catch (error) {
    store.dispatch('showNotification', {
      message: 'アカウントの削除に失敗しました',
      type: 'error'
    })
  } finally {
    showDeleteConfirmation.value = false
    confirmationText.value = ''
  }
}

const exportData = async () => {
  isExporting.value = true
  exportStatus.value = 'エクスポート処理中...'
  try {
    const result = await store.dispatch('auth/exportUserData')
    const blob = new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.style.display = 'none'
    a.href = url
    a.download = 'user_data_export.json'
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    exportStatus.value = 'エクスポートが完了しました'
  } catch (error) {
    console.error('Data export failed:', error)
    exportStatus.value = 'エクスポートに失敗しました'
    store.dispatch('showNotification', {
      message: 'データのエクスポートに失敗しました',
      type: 'error'
    })
  } finally {
    isExporting.value = false
  }
}
</script>