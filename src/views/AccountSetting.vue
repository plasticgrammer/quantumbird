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

    <v-card>
      <v-card-title>アカウント情報</v-card-title>
      <v-card-text>
        <v-text-field
          v-model="email"
          label="メールアドレス"
          readonly
          hide-details
          class="mb-4"
        ></v-text-field>

        <v-btn
          color="primary"
          variant="text"
          @click="showPasswordDialog = true"
        >
          パスワードを変更
          <v-icon class="ml-1" size="small">mdi-chevron-right</v-icon>
        </v-btn>
      </v-card-text>
    </v-card>

    <v-card class="mt-4">
      <v-card-title>データ管理</v-card-title>
      <v-card-text>
        <p class="mb-3">週次報告データをJSON形式でエクスポートします。</p>
        <v-btn color="info" :loading="isExporting" @click="exportData">
          <v-icon class="mr-2">mdi-download</v-icon>
          データをエクスポート
        </v-btn>
        <p v-if="exportStatus" class="mt-2">{{ exportStatus }}</p>
      </v-card-text>
    </v-card>

    <v-card class="mt-4">
      <v-card-title class="text-error">危険ゾーン</v-card-title>
      <v-card-text>
        <p class="mb-3">一度アカウントを削除すると、二度と元に戻せません。十分ご注意ください。</p>
        <v-btn color="error" @click="showDeleteConfirmation = true">
          <v-icon class="mr-2">mdi-account-off</v-icon>
          アカウントを削除
        </v-btn>
      </v-card-text>
    </v-card>

    <!-- パスワード変更ダイアログ -->
    <v-dialog v-model="showPasswordDialog" max-width="500px">
      <v-card>
        <v-card-title>パスワード変更</v-card-title>
        <v-card-text class="pb-2">
          <v-form ref="passwordForm" @submit.prevent="changePassword">
            <v-text-field
              v-model="passwordData.oldPassword"
              label="現在のパスワード"
              :type="showPassword ? 'text' : 'password'"
              :append-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
              :rules="[v => !!v || '現在のパスワードを入力してください']"
              hide-details="auto"
              class="mb-4"
              @click:append="showPassword = !showPassword"
            ></v-text-field>

            <v-text-field
              v-model="passwordData.newPassword"
              label="新しいパスワード"
              :type="showNewPassword ? 'text' : 'password'"
              :append-icon="showNewPassword ? 'mdi-eye' : 'mdi-eye-off'"
              :rules="passwordRules"
              hide-details="auto"
              class="mb-4"
              @click:append="showNewPassword = !showNewPassword"
            ></v-text-field>

            <v-text-field
              v-model="passwordData.confirmPassword"
              label="新しいパスワード（確認）"
              :type="showNewPassword ? 'text' : 'password'"
              :rules="[
                v => !!v || 'パスワードを確認してください',
                v => v === passwordData.newPassword || 'パスワードが一致しません'
              ]"
              hide-details="auto"
              class="mb-4"
            ></v-text-field>

            <div class="text-caption text-grey mb-2">
              パスワードは以下の要件を満たす必要があります：
              <ul class="ml-5 mt-1">
                <li>8文字以上</li>
                <li>大文字を含む</li>
                <li>小文字を含む</li>
                <li>数字を含む</li>
              </ul>
            </div>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="primary"
            variant="text"
            @click="showPasswordDialog = false"
          >
            キャンセル
          </v-btn>
          <v-btn
            color="primary"
            :loading="isChangingPassword"
            :disabled="isChangingPassword"
            @click="changePassword"
          >
            変更する
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

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
import { exportReports } from '../services/reportService'

const store = useStore()
const router = useRouter()
const passwordForm = ref(null)
const organizationId = store.getters['auth/organizationId']

const email = ref('')
const showDeleteConfirmation = ref(false)
const confirmationText = ref('')
const isExporting = ref(false)
const exportStatus = ref('')

const showPasswordDialog = ref(false)
const showPassword = ref(false)
const showNewPassword = ref(false)
const isChangingPassword = ref(false)
const passwordData = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// パスワードのバリデーションルール
const passwordRules = [
  v => !!v || 'パスワードを入力してください',
  v => v.length >= 8 || 'パスワードは8文字以上である必要があります',
  v => /[A-Z]/.test(v) || '大文字を含める必要があります',
  v => /[a-z]/.test(v) || '小文字を含める必要があります',
  v => /[0-9]/.test(v) || '数字を含める必要があります'
]

const user = computed(() => store.state.auth.user)

onMounted(() => {
  email.value = user.value.email
  // 他の設定フィールドの初期化
})

const changePassword = async () => {
  if (!passwordForm.value.validate()) return

  isChangingPassword.value = true
  try {
    await store.dispatch('auth/updatePassword', {
      oldPassword: passwordData.value.oldPassword,
      newPassword: passwordData.value.newPassword
    })

    store.dispatch('showNotification', {
      message: 'パスワードが正常に変更されました',
      type: 'success'
    })

    resetPasswordForm()
    showPasswordDialog.value = false
  } catch (error) {
    let errorMessage = 'パスワードの変更に失敗しました'
    if (error.message === 'Incorrect username or password.') {
      errorMessage = '現在のパスワードが正しくありません'
    }
    store.dispatch('showNotification', {
      message: errorMessage,
      type: 'error'
    })
  } finally {
    isChangingPassword.value = false
  }
}

const resetPasswordForm = () => {
  passwordData.value = {
    oldPassword: '',
    newPassword: '',
    confirmPassword: ''
  }
  passwordForm.value?.reset()
}

const deleteAccount = async () => {
  try {
    await store.dispatch('auth/deleteUserAccount')
    store.dispatch('showNotification', {
      message: 'アカウントが削除されました',
      type: 'success'
    })
    router.push({ name: 'SignIn' })
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
    const result = await exportReports(organizationId)
    const blob = new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.style.display = 'none'
    a.href = url
    a.download = 'weekly_report.json'
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