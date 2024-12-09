<template>
  <v-container class="account-management-container">
    <v-row dense class="pb-4">
      <v-col>
        <h3>
          <v-icon size="large" class="mr-1">
            mdi-account-cog
          </v-icon>
          組織アカウント管理
        </h3>
      </v-col>
    </v-row>

    <v-card 
      class="account-card pt-4 px-md-6"
      outlined
    >
      <v-form
        ref="form"
        v-model="isFormValid"
        @submit.prevent="handleSubmit"
      >
        <!-- アカウントリスト -->
        <div class="d-flex justify-space-between align-center mb-2">
          <div class="text-subtitle-1">
            登録アカウント数: {{ accounts.length }} / {{ maxAccountCount }}
          </div>
        </div>

        <v-card elevation="0" class="pa-1">
          <v-skeleton-loader
            v-if="loading"
            elevation="4"
            type="table-tbody"
          />
          
          <v-data-table
            v-else
            :headers="headers"
            :items="accounts"
            :loading="loading"
            hide-default-footer
            :items-per-page="-1"
            class="account-table"
          >
            <template #[`item.status`]="{ item }">
              <v-chip
                :color="getStatusColor(item.status)"
                size="small"
              >
                {{ getStatusLabel(item.status) }}
              </v-chip>
            </template>
            <template #[`item.actions`]="{ item }">
              <v-btn
                v-if="item.status === 'FORCE_CHANGE_PASSWORD'"
                icon
                small
                :disabled="loading"
                @click="handleResendInvitation(item)"
              >
                <v-icon>mdi-email</v-icon>
              </v-btn>
              <v-btn
                icon
                small
                :disabled="loading"
                @click="handleDeleteAccount(item)"
              >
                <v-icon>mdi-delete</v-icon>
              </v-btn>
            </template>
          </v-data-table>
        </v-card>

        <v-divider class="mb-4" />

        <!-- 新規アカウント作成フォーム -->
        <v-row v-if="isNew" class="mt-6 px-3">
          <v-col cols="12">
            <h4>新規アカウント作成</h4>
          </v-col>
          <v-col cols="12" sm="4">
            <v-text-field
              v-model="organizationId"
              label="組織ID"
              outlined
              dense
              :rules="[validateOrganizationId]"
              required
              @input="clearErrorMessage"
            />
          </v-col>
          <v-col cols="12" sm="4">
            <v-text-field
              v-model="account.organizationName"
              label="組織名"
              outlined
              dense
              :rules="[v => !!v || '組織名は必須です']"
              required
              @input="validateForm"
            />
          </v-col>
          <v-col cols="12" sm="4">
            <v-text-field
              v-model="account.email"
              label="メールアドレス"
              outlined
              dense
              :rules="[
                v => !!v || 'メールアドレスは必須です',
                v => isValidEmail(v) || '有効なメールアドレスを入力してください'
              ]"
              required
              @input="validateForm"
            />
          </v-col>
        </v-row>

        <v-row class="mt-2">
          <v-col cols="12" class="d-flex justify-end">
            <v-btn 
              color="primary" 
              type="submit" 
              :loading="loading"
              :disabled="!isFormValid"
            >
              <v-icon class="mr-1">mdi-account-plus</v-icon>
              アカウントを作成
            </v-btn>
          </v-col>
        </v-row>
      </v-form>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref, inject, onMounted, computed } from 'vue'
import { useStore } from 'vuex'
import { isValidEmail, validateOrganizationId } from '../utils/string-utils'
import { createAccount, getAccounts, deleteAccount, resendInvitation } from '../services/accountService'
import { deleteOrganizationCompletely } from '../services/organizationService'

const store = useStore()
const form = ref(null)
const showConfirmDialog = inject('showConfirmDialog')
const showNotification = inject('showNotification')
const showError = inject('showError')

const organizationId = ref('')
const account = ref({
  organizationName: '',
  email: ''
})
const accounts = ref([])
const loading = ref(false)
const isNew = ref(true)
const isFormValid = ref(false)

const headers = [
  { title: '組織ID', key: 'organizationId', align: 'start' },
  { title: '組織名', key: 'organizationName' },
  { title: 'メールアドレス', key: 'email' },
  { title: 'ステータス', key: 'status' },
  { title: '操作', key: 'actions', sortable: false }
]

const getStatusColor = (status) => {
  switch (status) {
  case 'CONFIRMED': return 'success'
  case 'FORCE_CHANGE_PASSWORD': return 'warning'
  default: return 'error'
  }
}

const getStatusLabel = (status) => {
  switch (status) {
  case 'CONFIRMED': return '有効'
  case 'FORCE_CHANGE_PASSWORD': return '初期設定待ち'
  default: return '無効'
  }
}

const validateForm = async () => {
  if (!form.value) return
  const validation = await form.value.validate()
  isFormValid.value = validation.valid
}

const clearErrorMessage = () => {
  validateForm()
}

const currentOrganizationId = store.getters['auth/organizationId']

const loadAccounts = async () => {
  loading.value = true
  try {
    accounts.value = await getAccounts({ parentOrganizationId: currentOrganizationId })
  } catch (error) {
    showError('アカウント情報の取得に失敗しました', error)
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  if (!isFormValid.value) return

  // サブスクリプション上限チェック
  const subscription = store.getters['auth/currentSubscription']
  if (accounts.value.length >= subscription.accountCount) {
    showError(
      `現在のプランでは${subscription.accountCount}アカウントまでしか作成できません。プランをアップグレードしてください。`
    )
    return
  }

  loading.value = true
  try {
    await createAccount({
      organizationId: organizationId.value,
      ...account.value,
      parentOrganizationId: currentOrganizationId
    })
    showNotification('アカウントを作成しました')

    await loadAccounts()
    // フォームをリセット
    organizationId.value = ''
    account.value = { organizationName: '', email: '' }
    isFormValid.value = false
    // フォームの検証状態をリセット
    if (form.value) {
      form.value.reset()
    }
  } catch (error) {
    showError('アカウントの作成に失敗しました', error)
  } finally {
    loading.value = false
  }
}

const handleDeleteAccount = async (accountItem) => {
  const organizationName = accountItem.organizationName || accountItem.organizationId || '未設定'
  
  const confirmed = await showConfirmDialog(
    '確認',
    `${organizationName}のアカウントと組織情報を削除しますか？\nこの操作は取り消せません。`
  )
  if (!confirmed) return

  loading.value = true
  try {
    
    // Cognitoユーザーを削除
    await deleteAccount(accountItem.organizationId)
    // 組織情報とすべての関連データを削除
    await deleteOrganizationCompletely(accountItem.organizationId)

    showNotification('アカウントと組織情報を削除しました')
    await loadAccounts()
  } catch (error) {
    showError('アカウントの削除に失敗しました', error)
  } finally {
    loading.value = false
  }
}

const handleResendInvitation = async (accountItem) => {
  loading.value = true
  try {
    await resendInvitation(accountItem.email)
    showNotification('招待メールを再送信しました')
  } catch (error) {
    showError('招待メールの再送信に失敗しました', error)
  } finally {
    loading.value = false
  }
}

const maxAccountCount = computed(() => {
  return store.getters['auth/currentSubscription'].accountCount
})

onMounted(loadAccounts)
</script>

<style scoped>
.account-management-container {
  max-width: 960px;
}

.account-card {
  background-color: white;
  border-radius: 0.5rem;
  padding: 0.5em 1em 1em;
}

.account-table {
  width: 100%;
}
</style>