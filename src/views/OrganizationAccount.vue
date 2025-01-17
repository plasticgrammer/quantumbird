<template>
  <v-container v-if="hasAccess" class="account-management-container">
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
        <div class="d-flex justify-end mb-4">
          <div class="text-subtitle-1">
            登録アカウント数: <span class="ml-1 font-weight-bold">{{ accounts.length }} / {{ maxAccountCount }}</span>
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
            :loading="loading"
            :headers="headers"
            :items="accounts"
            :items-per-page="-1"
            hide-default-footer
            class="account-table text-body-2 elevation-4 mobile-responsive-table"
          >
            <template #no-data>
              <div class="d-flex flex-column align-center py-6">
                <v-icon size="48" color="grey-lighten-1" class="mb-2">
                  mdi-account-group-outline
                </v-icon>
                <div class="text-grey">アカウントが登録されていません</div>
              </div>
            </template>
            <template #[`item.organizationId`]="{ item }">
              <v-text-field
                :value="item.organizationId"
                dense
                hide-details
                readonly
              />
            </template>
            <template #[`item.organizationName`]="{ item }">
              <v-text-field
                v-model="item.organizationName"
                outlined
                dense
                hide-details
                :readonly="editingAccount?.organizationId !== item.organizationId"
                required
              />
            </template>
            <template #[`item.email`]="{ item }">
              <v-text-field
                v-model="item.email"
                outlined
                dense
                hide-details
                :readonly="editingAccount?.organizationId !== item.organizationId"
                required
              >
                <template #append>
                  <v-icon
                    v-tooltip:top="getStatusLabel(item.status)"
                    :color="getStatusColor(item.status)"
                  >
                    {{ getStatusIcon(item.status) }}
                  </v-icon>
                </template>
              </v-text-field>
            </template>
            <template #[`item.actions`]="{ item }">
              <div class="d-flex justify-end">
                <v-btn
                  v-if="item.status === 'FORCE_CHANGE_PASSWORD'"
                  v-tooltip:top="'招待メールを再送信'"
                  icon
                  small
                  :disabled="loading"
                  @click="handleResendInvitation(item)"
                >
                  <v-icon>mdi-email</v-icon>
                </v-btn>
                <template v-if="editingAccount?.organizationId === item.organizationId">
                  <v-btn
                    v-tooltip:top="'キャンセル'"
                    icon
                    small
                    :disabled="loading"
                    @click="cancelEdit"
                  >
                    <v-icon>mdi-close</v-icon>
                  </v-btn>
                  <v-btn
                    v-tooltip:top="'保存'"
                    icon
                    small
                    :disabled="loading"
                    @click="handleSaveEdit(item)"
                  >
                    <v-icon color="success">mdi-check</v-icon>
                  </v-btn>
                </template>
                <template v-else>
                  <v-btn
                    v-tooltip:top="'編集'"
                    icon
                    small
                    :disabled="loading"
                    @click="handleEditAccount(item)"
                  >
                    <v-icon>mdi-pencil</v-icon>
                  </v-btn>
                  <v-btn
                    v-tooltip:top="'削除'"
                    icon
                    small
                    :disabled="loading"
                    @click="handleDeleteAccount(item)"
                  >
                    <v-icon>mdi-delete</v-icon>
                  </v-btn>
                </template>
              </div>
            </template>
          </v-data-table>
        </v-card>

        <!-- アカウント編集/作成フォーム -->
        <v-row class="mt-4">
          <v-col cols="12" sm="3">
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
          <v-col cols="12" sm="5">
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
              アカウント作成
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
import { createAccount, getAccounts, deleteAccount, resendInvitation, updateAccount } from '@/services/accountService'
import { deleteOrganizationCompletely } from '@/services/organizationService'
import { isValidEmail, validateOrganizationId } from '@/utils/string-utils'
import { getCurrentPlan } from '@/config/plans'

const store = useStore()
const form = ref(null)
const showConfirmDialog = inject('showConfirmDialog')
const showNotification = inject('showNotification')
const showError = inject('showError')

const currentOrganizationId = store.getters['auth/organizationId']
const organizationId = ref('')
const account = ref({
  organizationName: '',
  email: ''
})
const accounts = ref([])
const loading = ref(false)
const isFormValid = ref(false)
const editingAccount = ref(null)
const originalAccount = ref(null)

const headers = [
  { title: '組織ID', key: 'organizationId', width: '130px' },
  { title: '組織名', key: 'organizationName' },
  { title: 'メールアドレス', key: 'email' },
  { title: '操作', key: 'actions', align: 'center', sortable: false, width: '130px' }
]

const getStatusIcon = (status) => {
  switch (status) {
  case 'CONFIRMED': return 'mdi-check-circle'
  case 'FORCE_CHANGE_PASSWORD': return 'mdi-account-clock-outline'
  default: return 'mdi-alert-circle'
  }
}

const getStatusColor = (status) => {
  switch (status) {
  case 'CONFIRMED': return 'success'
  case 'FORCE_CHANGE_PASSWORD': return 'grey'
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

// エラーメッセージを抽出する関数を追加
const getErrorMessage = (error) => {
  return error?.response?.data?.message || error?.message || ''
}

const handleSubmit = async () => {
  if (!isFormValid.value) return

  // サブスクリプション上限チェック
  const subscription = store.getters['auth/currentSubscription']
  if (accounts.value.length >= subscription.accountCount) {
    showError(`現在のプランでは${subscription.accountCount}アカウントまでしか作成できません。プランをアップグレードしてください。`)
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

    // フォームをリセット
    organizationId.value = ''
    account.value = { organizationName: '', email: '' }
    isFormValid.value = false
    // フォームの検証状態をリセット
    if (form.value) {
      form.value.reset()
    }
    
    await loadAccounts()

  } catch (error) {
    const errorDetail = getErrorMessage(error)
    const message = `アカウントの作成に失敗しました${errorDetail ? `（${errorDetail}）` : ''}`
    showError(message, error)
  } finally {
    loading.value = false
  }
}

const handleDeleteAccount = async (accountItem) => {
  const organizationName = accountItem.organizationName || accountItem.organizationId || '未設定'
  
  const confirmed = await showConfirmDialog(
    '削除確認',
    `${organizationName}のアカウントと組織情報を削除しますか？\nこの操作は取り消せません。`,
    'error'
  )
  if (!confirmed) return

  loading.value = true
  try {
    // Cognitoユーザーを削除
    await deleteAccount(accountItem.organizationId, accountItem.email)
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
  try {
    await resendInvitation(accountItem.email)
    showNotification('招待メールを再送信しました')
  } catch (error) {
    showError('招待メールの再送信に失敗しました', error)
  }
}

const handleEditAccount = (item) => {
  editingAccount.value = { ...item }
  originalAccount.value = { ...item }
}

const handleSaveEdit = async (item) => {
  try {
    // メールアドレスのバリデーション
    if (!isValidEmail(item.email)) {
      showError('有効なメールアドレスを入力してください')
      return
    }
    // 組織名の必須チェック
    if (!item.organizationName) {
      showError('組織名は必須です')
      return
    }

    await updateAccount({
      organizationId: item.organizationId,
      organizationName: item.organizationName,
      email: item.email,
      oldEmail: editingAccount.value.email
    })
    showNotification('アカウント情報を更新しました')
    editingAccount.value = null
    originalAccount.value = null
  } catch (error) {
    const errorDetail = getErrorMessage(error)
    const message = `アカウントの更新に失敗しました${errorDetail ? `（${errorDetail}）` : ''}`
    showError(message, error)
  }
}

const cancelEdit = () => {
  if (originalAccount.value && editingAccount.value) {
    const index = accounts.value.findIndex(a => a.organizationId === editingAccount.value.organizationId)
    if (index !== -1) {
      accounts.value[index] = { ...originalAccount.value }
    }
  }
  editingAccount.value = null
  originalAccount.value = null
}

const maxAccountCount = computed(() => {
  return store.getters['auth/currentSubscription'].accountCount
})

// アクセス権限チェック
const hasAccess = computed(() => {
  const isParentAccount = store.getters['auth/isParentAccount']
  const hasAccountManagement = getCurrentPlan().adminFeatures.accountManagement
  return isParentAccount && hasAccountManagement
})

// コンポーネントマウント時の処理
onMounted(async () => {
  if (!hasAccess.value) {
    showError('この機能は親組織アカウントのみが利用できます')
    return
  }
  await loadAccounts()
})
</script>

<style scoped>
.account-management-container {
  max-width: 960px;
  font-size: 0.875rem;
}

.account-card {
  background-color: white;
  border-radius: 0.5rem;
  padding: 0.5em 1em 1em;
}

.account-table {
  width: 100%;
}

.account-table :deep(.v-text-field input) {
  font-size: 0.925rem !important;
  padding: 4px 8px !important;
}

.account-table :deep(.v-data-table-header__content) {
  padding-left: 8px !important;
}

@media (max-width: 600px) {
  .v-row .v-col-12 {
    padding: 4px !important;
  }

  .v-row .v-col-12:has(button) {
    padding: 16px !important;
  }

  .mobile-responsive-table :deep(.v-data-table__wrapper) {
    overflow-x: hidden;
  }

  .mobile-responsive-table :deep(tr) {
    display: grid;
    grid-template-columns: 1fr;
    padding: 8px;
    border-bottom: 1px solid rgba(0, 0, 0, 0.12);
  }

  .mobile-responsive-table :deep(td) {
    padding: 4px 8px !important;
    border-bottom: none !important;
    height: auto !important;
    display: flex;
    align-items: center;
  }

  .mobile-responsive-table :deep(thead) {
    display: none;
  }

  .mobile-responsive-table :deep(.v-text-field) {
    width: 100%;
    max-width: none;
  }

  .mobile-responsive-table :deep(.v-text-field__slot input) {
    min-width: 0;
  }
}
</style>