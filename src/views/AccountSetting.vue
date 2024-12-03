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
        <v-row>
          <v-col cols="6">
            <v-text-field
              v-model="email"
              label="メールアドレス"
              readonly
              hide-details
              class="mb-4"
            ></v-text-field>
          </v-col>
          <v-col cols="3">
            <v-text-field
              v-model="organizationId"
              label="組織ID"
              readonly
              hide-details
              class="mb-4"
            ></v-text-field>
          </v-col>
        </v-row>

        <v-btn
          color="primary"
          variant="text"
          @click="showPasswordDialog = true"
        >
          パスワードを変更
          <v-icon class="ml-1" size="small">mdi-chevron-right</v-icon>
        </v-btn>

        <v-card class="mt-4 mb-2" elevation="0" color="indigo-lighten-5 border-thin" outlined>
          <v-card-title>お支払い設定</v-card-title>
          <v-card-text class="px-6">
            <v-row align="center">
              <v-col>
                <div class="d-flex align-center">
                  <p class="mb-0 mr-4">現在のプラン：{{ currentPlanName }}</p>
                  <v-chip
                    v-if="isTrialPeriod"
                    color="warning"
                    size="small"
                    class="mr-2"
                  >
                    トライアル期間中
                  </v-chip>
                </div>
                <p class="text-caption text-grey mt-1">
                  プランの変更、支払い履歴の確認、請求書のダウンロードは支払い設定ページで行えます。
                </p>
              </v-col>
              <v-col cols="auto">
                <v-btn color="primary" @click="router.push({ name: 'Billing' })">
                  <v-icon class="mr-2">mdi-currency-usd</v-icon>
                  支払い設定
                </v-btn>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-card-text>
    </v-card>

    <v-card class="mt-4">
      <v-card-title>データ管理</v-card-title>
      <v-card-text class="px-6">
        <p class="mb-3">週次報告データをJSON形式でエクスポートします。</p>
        <v-btn color="info" :loading="isExporting" @click="exportData">
          <v-icon class="mr-2">mdi-download</v-icon>
          データをエクスポート
        </v-btn>
        <p v-if="exportStatus" class="mt-2">{{ exportStatus }}</p>
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
    <v-card class="mt-4">
      <v-card-title class="text-error">危険ゾーン</v-card-title>
      <v-card-text class="px-6">
        <div class="d-flex flex-column gap-4">
          <!-- アカウント引き継ぎ -->
          <div class="border-bottom pb-6">
            <p class="mb-2">アカウント引き継ぎ用にユーザー削除を行います。新しいユーザーに組織の管理を移譲できます。</p>
            <v-btn 
              color="error" 
              @click="showDeleteDialog = true"
            >
              <v-icon class="mr-2">mdi-account-switch</v-icon>
              アカウント引き継ぎ用の削除
            </v-btn>
          </div>

          <!-- アカウント完全削除 -->
          <div>
            <p class="mb-2 text-error">
              アカウントと全てのデータを完全に削除します。
            </p>
            <v-btn 
              color="error" 
              @click="showDeleteAllDialog = true"
            >
              <v-icon class="mr-2">mdi-account-off</v-icon>
              アカウントを完全に削除
            </v-btn>
          </div>
        </div>
      </v-card-text>
    </v-card>

    <!-- アカウント引き継ぎダイアログ -->
    <v-dialog v-model="showDeleteDialog" max-width="500px">
      <v-card>
        <v-card-title>アカウント引き継ぎ用 削除</v-card-title>
        <v-card-text>
          アカウントの引き継ぎを行うと：
          <div class="mb-4">
            <ul class="ml-4">
              <li>ユーザーアカウント情報、組織情報は削除されます</li>
              <li>メンバー情報、週次報告履歴は保持されます</li>
              <li>削除後に組織ID「<span class="text-error">{{ organizationId }}</span>」でサインアップしたユーザーが、<br>組織の新しい管理者となります</li>
            </ul>
            この操作は取り消すことができません。
          </div>
          <v-text-field
            v-model="deleteConfirmText"
            label="確認のため 'DELETE' と入力してください"
            hide-details
          ></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" variant="text" @click="showDeleteDialog = false">
            キャンセル
          </v-btn>
          <v-btn
            color="error"
            :disabled="deleteConfirmText !== 'DELETE'"
            :loading="isDeleting"
            @click="deleteAccount"
          >
            削除する
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- アカウント完全削除ダイアログ -->
    <v-dialog v-model="showDeleteAllDialog" max-width="500px">
      <v-card>
        <v-card-title>アカウントの完全削除</v-card-title>
        <v-card-text>
          以下のデータが完全に削除されます：
          <div class="mb-4">
            <ul class="ml-4">
              <li>ユーザーアカウント情報</li>
              <li>組織、メンバー情報</li>
              <li>週次報告履歴</li>
            </ul>
            <span class="text-error">この操作は取り消すことができません。</span>
          </div>
          <v-text-field
            v-model="deleteConfirmText"
            label="確認のため 'DELETE-ALL' と入力してください"
            hide-details
          ></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" variant="text" @click="showDeleteAllDialog = false">
            キャンセル
          </v-btn>
          <v-btn
            color="error"
            :disabled="deleteConfirmText !== 'DELETE-ALL'"
            :loading="isDeleting"
            @click="deleteAccountCompletely"
          >
            完全に削除する
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, inject, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { exportReports } from '../services/reportService'
import { deleteOrganization, deleteOrganizationCompletely } from '../services/organizationService'
import { useStripe } from '../composables/useStripe'
import { cancelSubscription } from '../services/paymentService'

const store = useStore()
const router = useRouter()
const { plans } = useStripe() // plansを取得

const passwordForm = ref(null)
const organizationId = store.getters['auth/organizationId']

const email = ref('')
const showPasswordDialog = ref(false)
const showPassword = ref(false)
const showNewPassword = ref(false)
const isChangingPassword = ref(false)
const passwordData = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})
const isExporting = ref(false)
const exportStatus = ref('')
const showDeleteDialog = ref(false)
const showDeleteAllDialog = ref(false)
const isDeleting = ref(false)
const deleteConfirmText = ref('')

const showConfirmDialog = inject('showConfirmDialog')

// 現在のプラン名を取得する computed プロパティ
const currentPlanName = computed(() => {
  const subscription = store.getters['auth/currentSubscription']
  const plan = plans.find(p => p.planId === subscription?.planId)
  return plan?.name || 'フリープラン'
})

// isTrialPeriod computed propertyを追加
const isTrialPeriod = computed(() => {
  const subscription = store.getters['auth/currentSubscription']
  return subscription?.trialEnd && new Date(subscription.trialEnd) > new Date()
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

const changeToFreePlan = async () => {
  const subscription = store.getters['auth/currentSubscription']
  // フリープランの場合はスキップ
  if (!subscription?.stripeCustomerId || subscription.planId === 'free') {
    return
  }

  await cancelSubscription(subscription.stripeCustomerId)
  await store.dispatch('auth/updateSubscriptionAttributes', {
    planId: 'free',
    accountCount: null,
    stripeCustomerId: subscription.stripeCustomerId
  })
}

const deleteAccount = async () => {
  const confirmed = await showConfirmDialog('確認', 'アカウントを削除します。よろしいですか？')
  if (!confirmed) return

  isDeleting.value = true
  try {
    // Cognitoユーザの削除を後にしないとトークンが無効となる
    await changeToFreePlan()
    await deleteOrganization(organizationId)
    
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
    isDeleting.value = false
    showDeleteDialog.value = false
    deleteConfirmText.value = ''
  }
}

const deleteAccountCompletely = async () => {
  const confirmed = await showConfirmDialog('確認', 'アカウントとすべてのデータを削除します。よろしいですか？')
  if (!confirmed) return

  isDeleting.value = true
  try {
    // Cognitoユーザの削除を後にしないとトークンが無効となる
    await changeToFreePlan()
    await deleteOrganizationCompletely(organizationId)

    await store.dispatch('auth/deleteUserAccount')

    store.dispatch('showNotification', {
      message: 'アカウントとすべてのデータが削除されました',
      type: 'success'
    })
    router.push({ name: 'SignIn' })
  } catch (error) {
    store.dispatch('showNotification', {
      message: 'アカウントの完全削除に失敗しました',
      type: 'error'
    })
  } finally {
    isDeleting.value = false
    showDeleteAllDialog.value = false
    deleteConfirmText.value = ''
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
  } finally {
    isExporting.value = false
  }
}

onMounted(async () => {
  email.value = user.value.email
})
</script>