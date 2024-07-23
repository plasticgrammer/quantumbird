<template>
  <v-container class="organization-management-container">
    <v-card 
      class="organization-card"
      elevation="4"
      outlined
    >
      <v-form @submit.prevent="handleSubmit">
        <v-text-field
          v-model="organization.organizationId"
          label="組織ID"
          outlined
          dense
        ></v-text-field>
        <v-text-field
          v-model="organization.name"
          label="組織名"
          outlined
          dense
          class="organization-name-input"
        ></v-text-field>

        <v-table class="members-table">
          <thead>
            <tr>
              <th class="text-left"></th>
              <th class="text-left">ID</th>
              <th class="text-left">名前</th>
              <th class="text-left">メールアドレス</th>
              <th class="text-left" style="width: 260px;"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="member in organization.members" :key="member.id">
              <td>
                <v-icon size="x-large">mdi-account-circle</v-icon>
              </td>
              <td>
                <v-text-field
                  v-model="member.id"
                  dense
                  readonly
                  variant="plain"
                  hide-details
                  class="member-id-input"
                ></v-text-field>
              </td>
              <td>
                <v-text-field
                  v-model="member.name"
                  outlined
                  dense
                  :readonly="editingMember?.id !== member.id"
                  :variant="editingMember?.id !== member.id ? 'plain' : 'outlined'"
                  hide-details
                  class="member-name-input"
                ></v-text-field>
              </td>
              <td>
                <v-text-field
                  v-model="member.email"
                  outlined
                  dense
                  :readonly="editingMember?.id !== member.id"
                  :variant="editingMember?.id !== member.id ? 'plain' : 'outlined'"
                  hide-details
                  class="member-email-input"
                ></v-text-field>
              </td>
              <td>
                <v-row no-gutters>
                  <v-col v-if="editingMember?.id === member.id">
                    <v-btn
                      small
                      color="primary"
                      @click="handleUpdateMember(member)"
                      class="mr-2"
                    >
                      保存
                    </v-btn>
                  </v-col>
                  <v-col v-else>
                    <v-btn
                      small
                      @click="setEditingMember(member)"
                      class="mr-2"
                    >
                      編集
                    </v-btn>
                    <v-btn
                      small
                      color="error"
                      @click="handleDeleteMember(member.id)"
                    >
                      削除
                    </v-btn>
                  </v-col>
                </v-row>
              </td>
            </tr>
            <tr class="newMember">
              <td></td>
              <td>
                <v-text-field
                  v-model="newMember.id"
                  label="ID"
                  :maxlength="8"
                  outlined
                  dense
                  hide-details
                  class="member-id-input mr-2"
                ></v-text-field>
              </td>
              <td>
                <v-text-field
                  v-model="newMember.name"
                  label="メンバー名"
                  outlined
                  dense
                  hide-details
                  class="member-name-input mr-2"
                ></v-text-field>
              </td>
              <td>
                <v-text-field
                  v-model="newMember.email"
                  label="メールアドレス"
                  outlined
                  dense
                  hide-details
                  class="member-email-input mr-2"
                ></v-text-field>
              </td>
              <td>
                <v-btn
                  color="primary"
                  @click="handleAddMember"
                >
                  メンバーを追加
                </v-btn>
              </td>
            </tr>
          </tbody>
        </v-table>

        <v-btn color="success" type="submit" class="mt-4" :loading="loading">
          <v-icon class="mr-1" left>mdi-check</v-icon>
          更新する
        </v-btn>
        <span class="px-3"></span>
        <v-btn color="grey lighten-1" @click="resetForm" class="mt-4" :disabled="loading">
          <v-icon class="mr-1" left>mdi-cancel</v-icon>
          更新しない
        </v-btn>
      </v-form>
    </v-card>

    <v-snackbar v-model="snackbar" :color="snackbarColor" :timeout="3000">
      {{ snackbarText }}
    </v-snackbar>
    
    <div v-if="true" class="debug-info">
      <h3>Debug Info:</h3>
      <pre>{{ JSON.stringify(organization, null, 2) }}</pre>
    </div>

  </v-container>
</template>

<script setup>
import { reactive, toRefs, onMounted } from 'vue'
import { useStore } from 'vuex'
import { submitOrganization, updateOrganization, getOrganization } from '../utils/organizationService'

const store = useStore()

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
  snackbar: false,
  snackbarText: '',
  snackbarColor: 'success'
})

const { organization, newMember, editingMember, loading, isNew, snackbar, snackbarText, snackbarColor } = toRefs(state)

const handleAddMember = () => {
  if (
    newMember.value.id.trim() !== '' &&
    newMember.value.name.trim() !== '' &&
    newMember.value.email.trim() !== ''
  ) {
    organization.value.members.push({
      id: newMember.value.id,
      name: newMember.value.name,
      email: newMember.value.email
    })
    console.log('Member added:', newMember.value)
    console.log('Updated members:', organization.value.members)
    newMember.value = { id: '', name: '', email: '' }
  }
}

const setEditingMember = (member) => {
  editingMember.value = member ? { ...member } : null
  console.log('Editing member:', editingMember.value)
}

const handleUpdateMember = (member) => {
  if (member.name.trim() !== '' && member.email.trim() !== '') {
    const index = organization.value.members.findIndex(m => m.id === member.id)
    if (index !== -1) {
      organization.value.members[index] = { ...member }
      console.log('Member updated:', member)
      console.log('Updated members:', organization.value.members)
    }
    editingMember.value = null
  }
}

const handleDeleteMember = (memberId) => {
  organization.value.members = organization.value.members.filter((member) => member.id !== memberId)
  console.log('Member deleted:', memberId)
  console.log('Updated members:', organization.value.members)
}

const handleSubmit = async () => {
  loading.value = true
  try {
    if (isNew.value) {
      await submitOrganization(organization.value)
      showSnackbar('新しい組織を作成しました', 'success')
    } else {
      await updateOrganization(organization.value)
      showSnackbar('組織情報を更新しました', 'success')
    }
    console.log('Organization submitted:', organization.value)
  } catch (error) {
    console.error('組織の保存に失敗しました:', error)
    showSnackbar('組織の保存に失敗しました', 'error')
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  organization.value = {
    organizationId: store.getters['user/organizationId'],
    name: '',
    members: []
  }
  newMember.value = { id: '', name: '', email: '' }
  editingMember.value = null
  console.log('Form reset, new organization state:', organization.value)
}

const showSnackbar = (text, color) => {
  snackbarText.value = text
  snackbarColor.value = color
  snackbar.value = true
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
        isNew.value = false
      } else {
        isNew.value = true
      }
    } catch (error) {
      console.error('組織情報の取得に失敗しました:', error)
      showSnackbar('組織情報の取得に失敗しました', 'error')
    } finally {
      loading.value = false
    }
  }
})
</script>

<style scoped>
.organization-management-container {
  min-width: 960px;
}

.organization-card {
  background-color: white;
  border-radius: 0.5rem;
  padding: 2rem;
}

.organization-name-input {
  font-size: 1.5rem;
}

.member-id-input {
  width: 100px;
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

.debug-info {
  margin-top: 20px;
  padding: 10px;
  background-color: #f0f0f0;
  border: 1px solid #ccc;
  border-radius: 4px;
}
</style>