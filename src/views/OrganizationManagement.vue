<template>
  <v-container class="organization-management-container">
    <v-row 
      dense 
      class="pb-4"
    >
      <v-col>
        <h3>
          <v-icon 
            size="large" 
            class="mr-1"
          >
            mdi-domain
          </v-icon>
          組織情報管理
        </h3>
      </v-col>
    </v-row>

    <v-card 
      class="organization-card"
      outlined
    >
      <v-form
        ref="form"
        v-model="isFormValid"
        @submit.prevent="handleSubmit"
      >
        <v-row class="mt-2">
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

        <v-skeleton-loader
          v-if="loading"
          elevation="4"
          type="table-tbody"
        />

        <v-card elevation="0" class="pa-1">
          <v-card 
            v-for="member in organization.members" 
            :key="member.id"
            variant="flat"
          >
            <v-card-text class="member-row px-3 py-1">
              <v-row>
                <v-col cols="12" sm="2" class="px-2">
                  <v-text-field
                    v-model="member.id"
                    label="ID"
                    dense
                    hide-details="auto"
                    readonly
                    class="member-id-input"
                  >
                    <template #prepend>
                      <v-icon size="x-large">
                        mdi-account-box-outline
                      </v-icon>
                    </template>
                  </v-text-field>
                </v-col>
                <v-col cols="12" sm="3" class="px-2">
                  <v-text-field
                    v-model="member.name"
                    label="名前"
                    outlined
                    dense
                    hide-details="auto"
                    :readonly="editingMember?.id !== member.id"
                    :error-messages="editingMember?.id === member.id ? editValidationErrors.name : ''"
                  />
                </v-col>
                <v-col cols="12" sm="5" class="px-2">
                  <v-text-field
                    v-model="member.email"
                    label="メールアドレス"
                    outlined
                    dense
                    hide-details="auto"
                    :readonly="editingMember?.id !== member.id"
                    :error-messages="editingMember?.id === member.id ? editValidationErrors.email : ''"
                  >
                    <template #append>
                      <v-icon v-if="member.mailConfirmed" color="success">
                        mdi-email-check-outline
                      </v-icon>
                      <v-icon v-else>
                        mdi-email-search-outline
                      </v-icon>
                      <v-tooltip activator="parent" location="top">
                        メール{{ member.mailConfirmed ? '確認済み' : '確認中' }}
                      </v-tooltip>
                    </template>
                  </v-text-field>
                </v-col>
                <v-col cols="12" sm="2" class="d-flex justify-end">
                  <v-btn v-if="editingMember?.id === member.id" icon small @click="handleUpdateMember(member)">
                    <v-icon>mdi-check</v-icon>
                  </v-btn>
                  <v-btn v-else icon small @click="setEditingMember(member)">
                    <v-icon>mdi-pencil</v-icon>
                  </v-btn>
                  <v-btn icon small @click="handleDeleteMember(member.id)">
                    <v-icon>mdi-delete</v-icon>
                  </v-btn>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-card>

        <v-row class="mt-4 mx-3 align-center">
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
              @click="handleAddMember"
            >
              メンバーを追加
            </v-btn>
          </v-col>
        </v-row>

        <div class="mt-5">
          <v-btn 
            color="primary" 
            type="submit" 
            :loading="loading"
            :disabled="!isFormValid || !!editingMember || !isFormChanged"
          >
            <v-icon
              class="mr-1"
              left
            >
              mdi-check
            </v-icon>
            更新する
          </v-btn>
        </div>
      </v-form>
    </v-card>
  </v-container>
</template>

<script setup>
import { reactive, toRefs, ref, onMounted, inject, computed, watch } from 'vue'
import { useStore } from 'vuex'
import { submitOrganization, updateOrganization, getOrganization } from '../services/organizationService'

const store = useStore()
const form = ref(null)
const showConfirmDialog = inject('showConfirmDialog')
const showNotification = inject('showNotification')

const state = reactive({
  organization: {
    organizationId: store.getters['user/organizationId'],
    name: '',
    members: []
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
  originalOrganization: null
})

const { organization, newMember, editingMember, loading, isNew, isFormValid, isFormChanged, validationErrors, editValidationErrors } = toRefs(state)

const validateEmail = (email) => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return re.test(email)
}

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
  } else if (!validateEmail(member.email)) {
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

const setEditingMember = (member) => {
  editingMember.value = member ? { ...member } : null
  editValidationErrors.value = { name: '', email: '' }
}

const handleFormChange = () => {
  isFormChanged.value = true
}

const handleAddMember = () => {
  if (validateNewMember()) {
    organization.value.members.push({
      id: newMember.value.id,
      name: newMember.value.name,
      email: newMember.value.email
    })
    newMember.value = { id: '', name: '', email: '' }
    validationErrors.value = { id: '', name: '', email: '' }
    handleFormChange()
  }
}

const handleUpdateMember = (member) => {
  if (validateMember(member, editValidationErrors.value)) {
    const index = organization.value.members.findIndex(m => m.id === member.id)
    if (index !== -1) {
      organization.value.members[index] = { ...member }
    }
    editingMember.value = null
    editValidationErrors.value = { name: '', email: '' }
    handleFormChange()
  }
}

const handleDeleteMember = async (memberId) => {
  const confirmed = await showConfirmDialog('確認', '本当にこのメンバーを削除しますか？')
  if (confirmed) {
    organization.value.members = organization.value.members.filter((member) => member.id !== memberId)
    handleFormChange()
  }
}

const validateForm = async () => {
  const validation = await form.value.validate()
  isFormValid.value = validation.valid
}

const isOrganizationValid = computed(() => {
  return organization.value.name.trim() !== ''
})

const handleSubmit = async () => {
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
    console.log('Organization submitted:', organization.value)
    state.originalOrganization = JSON.parse(JSON.stringify(organization.value))
    isFormChanged.value = false
  } catch (error) {
    showNotification('組織の保存に失敗しました', error)
  }
}

onMounted(async () => {
  const organizationId = store.getters['user/organizationId']
  console.log('Mounted, organizationId:', organizationId)
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
      // フォームの初期バリデーション
      await validateForm()
    } catch (error) {
      showNotification('組織情報の取得に失敗しました', error)
    } finally {
      loading.value = false
    }
  }
})

// フォームの内容が変更されたかどうかを監視
watch(
  () => JSON.stringify(organization.value),
  (newVal) => {
    if (state.originalOrganization) {
      isFormChanged.value = newVal !== JSON.stringify(state.originalOrganization)
    }
  },
  { deep: true }
)
</script>

<style scoped>
.organization-management-container {
  max-width: 960px;
}

.organization-card {
  background-color: white;
  border-radius: 0.5rem;
  padding: 0.5em 1.5em 1em;
  position: relative;
}

.organization-name-input {
  font-size: 1.5rem;
}

.v-table th {
  font-weight: bold !important;
  color: rgba(0, 0, 0, 0.6) !important;
}

.v-table td {
  padding: 10px 10px !important;
}

.v-table .newMember td {
  padding: 30px 10px 10px !important;
}

@media (max-width: 600px) {
  .v-row .v-col-12 {
    padding: 4px !important;
  }

  .v-row .v-col-12:has(button) {
    padding: 16px !important;
  }

  .member-row {
    border-bottom: solid 1px lightgray;
  }
}
</style>