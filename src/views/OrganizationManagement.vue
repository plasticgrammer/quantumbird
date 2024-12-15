<template>
  <v-container class="organization-management-container">
    <v-row dense class="pb-4">
      <v-col>
        <h3>
          <v-icon size="large" class="mr-1">
            mdi-domain
          </v-icon>
          組織情報管理
        </h3>
      </v-col>
    </v-row>

    <v-card 
      class="organization-card px-md-6 rounded-lg"
      outlined
    >
      <v-form ref="form">
        <v-row class="mt-2 px-3">
          <v-col cols="12" sm="3">
            <v-text-field
              v-model="organization.organizationId"
              label="組織ID"
              variant="plain"
              outlined
              dense
              readonly
              hide-details
            />
          </v-col>
          <v-col cols="12" sm="9" class="d-flex align-center">
            <v-text-field
              v-model="organization.name"
              label="組織名"
              outlined
              dense
              class="organization-name-input flex-grow-1"
              :rules="[v => !!v || '組織名は必須です']"
              required
            />
            <div class="ml-2 mb-4" style="width: 50px">
              <v-btn 
                v-if="isOrgNameChanged"
                icon 
                small 
                @click="handleUpdateOrganization"
              >
                <v-icon color="teal">mdi-check</v-icon>
              </v-btn>
            </div>
          </v-col>
        </v-row>

        <v-card elevation="0" class="pa-1">
          <v-alert
            v-if="isMaxMembersReached"
            type="warning"
            density="compact"
            variant="tonal"
            class="mb-4"
          >
            メンバー数が上限（{{ getAdminFeatures.maxMembers }}名）に達しています。<br>
            より多くのメンバーを追加するには、プランのアップグレードが必要です。
          </v-alert>

          <v-skeleton-loader
            v-if="loading"
            elevation="4"
            type="table-tbody"
          />
          
          <v-data-table
            v-else
            :headers="headers"
            :items="organization.members"
            hide-default-footer
            :items-per-page="-1"
            class="member-table text-body-2 elevation-4"
          >
            <template #no-data>
              <div class="d-flex flex-column align-center py-6">
                <v-icon size="48" color="grey-lighten-1" class="mb-2">
                  mdi-account-group-outline
                </v-icon>
                <div class="text-grey">メンバーが登録されていません</div>
              </div>
            </template>
            <template #[`item.icon`]>
              <v-icon size="x-large">mdi-account-box-outline</v-icon>
            </template>
            <template #[`item.id`]="{ item }">
              <v-text-field
                :value="item.id"
                dense
                hide-details
                readonly
              >
              </v-text-field>
            </template>
            <template #[`item.name`]="{ item }">
              <v-text-field
                v-model="item.name"
                outlined
                dense
                hide-details
                :readonly="editingMember?.id !== item.id"
                :error-messages="editingMember?.id === item.id ? editValidationErrors.name : ''"
              />
            </template>
            <template #[`item.email`]="{ item }">
              <v-text-field
                v-model="item.email"
                outlined
                dense
                hide-details
                :readonly="editingMember?.id !== item.id"
                :error-messages="editingMember?.id === item.id ? editValidationErrors.email : ''"
              >
                <template #append>
                  <v-icon v-if="item.emailConfirmed" v-tooltip:top="'メール確認済み'" color="success">
                    mdi-check-circle
                  </v-icon>
                  <v-icon v-else v-tooltip:top="'メール確認中'" color="grey">
                    mdi-email-search-outline
                  </v-icon>
                </template>
              </v-text-field>
            </template>
            <template #[`item.actions`]="{ item }">
              <div class="d-flex justify-end">
                <template v-if="editingMember?.id === item.id">
                  <v-btn 
                    v-tooltip:top="'キャンセル'"
                    icon 
                    small 
                    @click="cancelEdit"
                  >
                    <v-icon>mdi-close</v-icon>
                  </v-btn>
                  <v-btn 
                    v-tooltip:top="'保存'"
                    icon 
                    small 
                    @click="handleUpdateMember(item)"
                  >
                    <v-icon color="teal">mdi-check</v-icon>
                  </v-btn>
                </template>
                <template v-else>
                  <v-btn 
                    v-tooltip:top="'編集'"
                    icon 
                    small 
                    @click="setEditingMember(item)"
                  >
                    <v-icon>mdi-pencil</v-icon>
                  </v-btn>
                  <v-btn 
                    v-tooltip:top="'削除'"
                    icon 
                    small 
                    @click="handleDeleteMember(item.id)"
                  >
                    <v-icon>mdi-delete</v-icon>
                  </v-btn>
                </template>
              </div>
            </template>
          </v-data-table>
        </v-card>

        <v-row class="mt-4 mx-0 align-center">
          <v-col cols="12" sm="2" class="px-1">
            <v-text-field
              v-model="newMember.id"
              label="ID"
              :maxlength="8"
              outlined
              dense
              color="primary"
              :error-messages="validationErrors.id"
              class="member-id-input mr-2"
            />
          </v-col>
          <v-col cols="12" sm="3" class="px-1">
            <v-text-field
              v-model="newMember.name"
              label="名前"
              outlined
              dense
              color="primary"
              :error-messages="validationErrors.name"
              class="member-name-input mr-2"
            />
          </v-col>
          <v-col cols="12" sm="5" class="px-1">
            <v-text-field
              v-model="newMember.email"
              label="メールアドレス"
              outlined
              dense
              color="primary"
              :error-messages="validationErrors.email"
              class="member-email-input mr-2"
            />
          </v-col>
          <v-col cols="12" sm="2" class="px-1">
            <v-btn
              color="primary"
              :disabled="isSubmitDisabled"
              @click="handleAddMember"
            >
              <v-icon class="mr-1">mdi-account-plus</v-icon>
              メンバー登録
            </v-btn>
          </v-col>
        </v-row>
      </v-form>
    </v-card>
  </v-container>
</template>

<script setup>
import { reactive, toRefs, ref, onMounted, inject, computed } from 'vue'
import { useStore } from 'vuex'
import { updateOrganization, getOrganization } from '../services/organizationService'
import { createMember, updateMember, deleteMember, listOrganizationMembers } from '../services/memberService'
import { isValidEmail } from '../utils/string-utils'
import { getCurrentPlan } from '../config/plans'

const store = useStore()
const form = ref(null)
const showConfirmDialog = inject('showConfirmDialog')
const showNotification = inject('showNotification')
const showError = inject('showError')

const state = reactive({
  organization: {
    organizationId: store.getters['auth/organizationId'],
    name: '',
    members: [],
  },
  newMember: { id: '', name: '', email: '' },
  editingMember: null,
  loading: false,
  isNew: true,
  validationErrors: {
    id: '',
    name: '',
    email: ''
  },
  editValidationErrors: {
    name: '',
    email: ''
  },
  originalMember: null,
  originalOrgName: '',
}) 

const { organization, newMember, editingMember, loading, isNew, validationErrors, editValidationErrors, originalMember, originalOrgName } = toRefs(state)

// テーブルのヘッダー定義を追加
const headers = [
  { title: '', key: 'icon', align: 'start', sortable: false, width: '30px' },
  { title: 'ID', key: 'id', align: 'start', width: '100px' },
  { title: '名前', key: 'name' },
  { title: 'メールアドレス', key: 'email' },
  { title: '操作', key: 'actions', align: 'center', sortable: false, width: '130px' }
]

// Inline definition of useOrganizationValidation
const useOrganizationValidation = (organization, newMember, validationErrors) => {
  const validateMember = (member, errors) => {
    let isValid = true

    if (!member.name.trim()) {
      errors.name = '名前は必須です'
      isValid = false
    } else {
      errors.name = ''
    }

    if (!member.email.trim()) {
      errors.email = 'メールアドレスは必須です'
      isValid = false
    } else if (!isValidEmail(member.email)) {
      errors.email = '有効なメールアドレスを入力してください'
      isValid = false
    } else {
      errors.email = ''
    }

    return isValid
  }

  const validateNewMember = () => {
    let isValid = validateMember(newMember.value, validationErrors.value)

    if (!newMember.value.id.trim()) {
      validationErrors.value.id = 'IDは必須です'
      isValid = false
    } else if (organization.value.members.some(member => member.id === newMember.value.id)) {
      validationErrors.value.id = '既に存在します'
      isValid = false
    } else {
      validationErrors.value.id = ''
    }

    return isValid
  }

  return { validateMember, validateNewMember }
}

const { validateMember, validateNewMember } = useOrganizationValidation(organization, newMember, validationErrors)

const getAdminFeatures = computed(() => {
  const currentPlan = getCurrentPlan()
  return currentPlan.adminFeatures
})

const isMaxMembersReached = computed(() => {
  const maxMembers = getAdminFeatures.value.maxMembers
  return maxMembers !== -1 && organization.value.members.length >= maxMembers
})

const isSubmitDisabled = computed(() => {
  return !newMember.value.id.trim() || 
         !newMember.value.name.trim() || 
         !newMember.value.email.trim() ||
         isMaxMembersReached.value
})

// Group related functions
const memberManagement = {
  setEditingMember(member) {
    editingMember.value = member ? { ...member } : null
    originalMember.value = member ? { ...member } : null
    editValidationErrors.value = { name: '', email: '' }
  },

  async handleAddMember() {
    if (isMaxMembersReached.value) {
      const maxMembers = getAdminFeatures.value.maxMembers
      showError('エラー', `現在のプランでは${maxMembers === -1 ? '無制限です。' : `最大${maxMembers}名まで`}しか登録できません。`)
      return
    }
    
    if (validateNewMember()) {
      const newMemberData = {
        id: newMember.value.id,
        name: newMember.value.name,
        email: newMember.value.email,
        organizationId: organization.value.organizationId
      }
      
      try {
        await createMember(newMemberData)
        organization.value.members.push(newMemberData)
        newMember.value = { id: '', name: '', email: '' }
        validationErrors.value = { id: '', name: '', email: '' }
        showNotification('メンバーを追加しました')
      } catch (error) {
        showError('メンバーの追加に失敗しました', error)
      }
    }
  },

  async handleUpdateMember(member) {
    if (validateMember(member, editValidationErrors.value)) {
      try {
        await updateMember({
          ...member,
          organizationId: organization.value.organizationId
        })
        const index = organization.value.members.findIndex(m => m.id === member.id)
        if (index !== -1) {
          organization.value.members[index] = { ...member }
        }
        editingMember.value = null
        originalMember.value = null
        editValidationErrors.value = { name: '', email: '' }
        showNotification('メンバー情報を更新しました')
      } catch (error) {
        showError('メンバー情報の更新に失敗しました', error)
      }
    }
  },

  async handleDeleteMember(memberId) {
    const confirmed = await showConfirmDialog('確認', 'このメンバーを削除しますか？')
    if (confirmed) {
      const member = organization.value.members.find(m => m.id === memberId)
      if (!member) return

      try {
        await deleteMember(member.memberUuid)
        organization.value.members = organization.value.members.filter(m => m.id !== memberId)
        showNotification('メンバーを削除しました')
      } catch (error) {
        showError('メンバーの削除に失敗しました', error)
      }
    }
  },

  cancelEdit() {
    if (originalMember.value && editingMember.value) {
      const index = organization.value.members.findIndex(m => m.id === editingMember.value.id)
      if (index !== -1) {
        organization.value.members[index] = { ...originalMember.value }
      }
    }
    editingMember.value = null
    originalMember.value = null
  }
}

// 組織名編集関連の関数
const isOrgNameChanged = computed(() => {
  return organization.value.name !== originalOrgName.value
})

const handleUpdateOrganization = async () => {
  if (!organization.value.name.trim()) return
  
  try {
    await updateOrganization({
      organizationId: organization.value.organizationId,
      name: organization.value.name
    })
    originalOrgName.value = organization.value.name
    showNotification('組織名を更新��ました')
  } catch (error) {
    showError('組織名の更新に失敗しました', error)
    organization.value.name = originalOrgName.value
  }
}

onMounted(async () => {
  const organizationId = store.getters['auth/organizationId']
  if (organizationId) {
    loading.value = true
    try {
      const [orgResult, membersResult] = await Promise.all([
        getOrganization(organizationId),
        listOrganizationMembers(organizationId)
      ])
      
      if (orgResult && Object.keys(orgResult).length > 0) {
        organization.value = {
          ...orgResult,
          members: membersResult || []
        }
        originalOrgName.value = orgResult.name
        isNew.value = false
      } else {
        isNew.value = true
      }
    } catch (error) {
      showError('組織情報の取得に失敗しました', error)
    } finally {
      loading.value = false
    }
  }
})

// Expose necessary functions and reactive references
const { setEditingMember, handleAddMember, handleUpdateMember, handleDeleteMember, cancelEdit } = memberManagement
</script>

<style scoped>
.organization-management-container {
  max-width: 960px;
}

.organization-card {
  background-color: white;
  padding: 0.5em 1em 1em;
  position: relative;
}

@media (max-width: 600px) {
  .v-row .v-col-12 {
    padding: 4px !important;
  }

  .v-row .v-col-12:has(button) {
    padding: 16px !important;
  }
}

.member-table {
  width: 100%;
}

.member-table :deep(.v-text-field input) {
  font-size: 0.925rem !important;
  padding: 4px 8px !important;
}

.member-table :deep(.v-data-table-header__content) {
  padding-left: 8px !important;
}
</style>