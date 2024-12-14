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
      <v-form
        ref="form"
        v-model="isFormValid"
        @submit.prevent="handleSubmit"
      >
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
          <v-col cols="12" sm="9">
            <v-text-field
              v-model="organization.name"
              label="組織名"
              outlined
              dense
              class="organization-name-input"
              :rules="[v => !!v || '組織名は必須です']"
              required
              @input="validateForm"
            />
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
                  <v-btn icon small @click="cancelEdit">
                    <v-icon>mdi-close</v-icon>
                  </v-btn>
                  <v-btn icon small @click="handleUpdateMember(item)">
                    <v-icon color="teal">mdi-check</v-icon>
                  </v-btn>
                </template>
                <template v-else>
                  <v-btn icon small @click="setEditingMember(item)">
                    <v-icon>mdi-pencil</v-icon>
                  </v-btn>
                  <v-btn icon small @click="handleDeleteMember(item.id)">
                    <v-icon>mdi-delete</v-icon>
                  </v-btn>
                </template>
              </div>
            </template>
          </v-data-table>
        </v-card>

        <v-row class="mt-4 mx-0 mx-md-3 align-center">
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
              color="secondary"
              :disabled="isMaxMembersReached"
              @click="handleAddMember"
            >
              メンバーを追加
            </v-btn>
          </v-col>
        </v-row>

        <v-row class="mt-2">
          <v-col cols="12" class="d-flex justify-end">
            <v-btn 
              color="primary" 
              type="submit" 
              :loading="loading"
              :disabled="!isFormValid || !!editingMember || !isFormChanged"
            >
              <v-icon class="mr-1">mdi-check</v-icon>
              更新する
            </v-btn>
          </v-col>
        </v-row>
      </v-form>
    </v-card>
  </v-container>
</template>

<script setup>
import { reactive, toRefs, ref, onMounted, inject, computed, watch } from 'vue'
import { useStore } from 'vuex'
import { submitOrganization, updateOrganization, getOrganization } from '../services/organizationService'
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
  isFormValid: false,
  isFormChanged: false,
  validationErrors: {
    id: '',
    name: '',
    email: ''
  },
  editValidationErrors: {
    name: '',
    email: ''
  },
  originalOrganization: null,
  originalMember: null, // 追加
})

const { organization, newMember, editingMember, loading, isNew, isFormValid, isFormChanged, validationErrors, editValidationErrors, originalMember } = toRefs(state)

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

// Computed property for organization validity
const isOrganizationValid = computed(() => {
  return organization.value.name.trim() !== ''
})

const getAdminFeatures = computed(() => {
  const currentPlan = getCurrentPlan()
  return currentPlan.adminFeatures
})

const isMaxMembersReached = computed(() => {
  const maxMembers = getAdminFeatures.value.maxMembers
  return maxMembers !== -1 && organization.value.members.length >= maxMembers
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
      organization.value.members.push({
        id: newMember.value.id,
        name: newMember.value.name,
        email: newMember.value.email
      })
      newMember.value = { id: '', name: '', email: '' }
      validationErrors.value = { id: '', name: '', email: '' }
      formManagement.handleFormChange()
    }
  },

  handleUpdateMember(member) {
    if (validateMember(member, editValidationErrors.value)) {
      const index = organization.value.members.findIndex(m => m.id === member.id)
      if (index !== -1) {
        organization.value.members[index] = { ...member }
      }
      editingMember.value = null
      originalMember.value = null
      editValidationErrors.value = { name: '', email: '' }
      formManagement.handleFormChange()
    }
  },

  async handleDeleteMember(memberId) {
    const confirmed = await showConfirmDialog('確認', '本当にこのメンバーを削除しますか？\n（更新するまでは確定されません）')
    if (confirmed) {
      organization.value.members = organization.value.members.filter((member) => member.id !== memberId)
      formManagement.handleFormChange()
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

// formManagementのhandleSubmitを修正
const formManagement = {
  handleFormChange() {
    isFormChanged.value = true
  },

  async validateForm() {
    if (!form.value) {
      isFormValid.value = false
      return
    }
    const validation = await form.value.validate()
    isFormValid.value = validation.valid
  },

  async handleSubmit() {
    if (!isOrganizationValid.value || !isFormChanged.value) {
      return
    }

    try {
      if (isNew.value) {
        await submitOrganization(organization.value)
        showNotification('組織情報を登録しました')
      } else {
        await updateOrganization(organization.value)
        showNotification('組織情報を更新しました')
      }
      state.originalOrganization = JSON.parse(JSON.stringify(organization.value))
      isFormChanged.value = false
    } catch (error) {
      showError('組織の保存に失敗しました', error)
    }
  }
}

onMounted(async () => {
  const organizationId = store.getters['auth/organizationId']
  if (organizationId) {
    loading.value = true
    try {
      const result = await getOrganization(organizationId)
      if (result && Object.keys(result).length > 0) {
        organization.value = result
        state.originalOrganization = JSON.parse(JSON.stringify(result))
        isNew.value = false
      } else {
        isNew.value = true
      }
      await formManagement.validateForm()
    } catch (error) {
      showError('組織情報の取得に失敗しました', error)
    } finally {
      loading.value = false
    }
  }
})

watch(
  () => JSON.stringify(organization.value),
  (newVal) => {
    if (state.originalOrganization) {
      isFormChanged.value = newVal !== JSON.stringify(state.originalOrganization)
    }
  },
  { deep: true }
)

// Expose necessary functions and reactive references
const { setEditingMember, handleAddMember, handleUpdateMember, handleDeleteMember, cancelEdit } = memberManagement
const { validateForm, handleSubmit } = formManagement
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