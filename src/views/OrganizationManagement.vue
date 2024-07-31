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
      elevation="4"
      outlined
    >
      <v-form
        ref="form"
        v-model="isFormValid"
        @submit.prevent="handleSubmit"
      >
        <v-row class="mt-2">
          <v-col cols="3">
            <v-text-field
              v-model="organization.organizationId"
              label="組織ID"
              variant="plain"
              outlined
              dense
              readonly
            />
          </v-col>
          <v-col cols="9">
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

        <v-card
          v-else
          elevation="4"
          class="px-1"
        >
          <v-table class="members-table">
            <thead>
              <tr>
                <th class="text-left" />
                <th class="text-left">
                  ID
                </th>
                <th class="text-left">
                  名前
                </th>
                <th class="text-left">
                  メールアドレス
                </th>
                <th
                  class="text-left"
                  style="width: 100px;"
                />
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="member in organization.members"
                :key="member.id"
              >
                <td>
                  <v-icon size="x-large">
                    mdi-account-box-outline
                  </v-icon>
                </td>
                <td>
                  <v-text-field
                    v-model="member.id"
                    dense
                    readonly
                    density="compact"
                    hide-details
                    class="member-id-input"
                  />
                </td>
                <td>
                  <v-text-field
                    v-model="member.name"
                    outlined
                    dense
                    density="compact"
                    :readonly="editingMember?.id !== member.id"
                    :error-messages="editingMember?.id === member.id ? editValidationErrors.name : ''"
                    hide-details="auto"
                    class="member-name-input"
                  />
                </td>
                <td>
                  <v-text-field
                    v-model="member.email"
                    outlined
                    dense
                    density="compact"
                    :readonly="editingMember?.id !== member.id"
                    :error-messages="editingMember?.id === member.id ? editValidationErrors.email : ''"
                    hide-details="auto"
                    class="member-email-input"
                  />
                </td>
                <td>
                  <v-row
                    no-gutters
                    justify="end"
                  >
                    <v-col v-if="editingMember?.id === member.id">
                      <v-btn
                        icon
                        small
                        class="action-btn"
                        @click="handleUpdateMember(member)"
                      >
                        <v-icon small>
                          mdi-check
                        </v-icon>
                      </v-btn>
                    </v-col>
                    <v-col v-else>
                      <v-btn
                        icon
                        small
                        class="mr-1 action-btn"
                        elevation="4"
                        @click="setEditingMember(member)"
                      >
                        <v-icon small>
                          mdi-pencil
                        </v-icon>
                      </v-btn>
                      <v-btn
                        icon
                        small
                        class="action-btn"
                        elevation="4"
                        @click="handleDeleteMember(member.id)"
                      >
                        <v-icon small>
                          mdi-delete
                        </v-icon>
                      </v-btn>
                    </v-col>
                  </v-row>
                </td>
              </tr>
              <tr class="newMember">
                <td />
                <td>
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
                </td>
                <td>
                  <v-text-field
                    v-model="newMember.name"
                    label="名前"
                    outlined
                    dense
                    color="primary"
                    :error-messages="validationErrors.name"
                    class="member-name-input mr-2"
                  />
                </td>
                <td>
                  <v-text-field
                    v-model="newMember.email"
                    label="メールアドレス"
                    outlined
                    dense
                    color="primary"
                    :error-messages="validationErrors.email"
                    class="member-email-input mr-2"
                  />
                </td>
                <td>
                  <v-btn
                    color="secondary"
                    @click="handleAddMember"
                  >
                    メンバーを追加
                  </v-btn>
                </td>
              </tr>
            </tbody>
          </v-table>
        </v-card>

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
import { reactive, toRefs, ref, onMounted, inject, watch } from 'vue'
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
    console.log('Member added:', newMember.value)
    console.log('Updated members:', organization.value.members)
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
  const confirmed = await showConfirmDialog('確認', '本当にこの項目を削除しますか？')
  if (confirmed) {
    organization.value.members = organization.value.members.filter((member) => member.id !== memberId)
    handleFormChange()
  }
}

const validateForm = async () => {
  const validation = await form.value.validate()
  isFormValid.value = validation.valid
}

const handleSubmit = async () => {
  await validateForm()
  
  if (!isFormValid.value || !isFormChanged.value) {
    return
  }

  loading.value = true
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
  } finally {
    loading.value = false
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
  min-width: 960px;
}

.organization-card {
  background-color: white;
  border-radius: 0.5rem;
  padding: .5em 1.5em 1em;
  position: relative;
}

.organization-name-input {
  font-size: 1.5rem;
}

.member-id-input {
  width: 120px;
}

.member-name-input {
  width: 160px;
}

.member-email-input {
  width: 300px;
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
</style>