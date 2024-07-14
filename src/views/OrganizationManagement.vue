<template>
  <v-app>
    <v-container class="organization-management-container">
      <v-card class="organization-card"
        elevation="4"
      >
        <v-form>
          <v-text-field
            v-model="organization.name"
            label="組織名"
            variant="outlined"
            class="organization-name-input"
            @input="handleOrganizationNameChange"
          ></v-text-field>
        </v-form>

        <div class="members-table-container">
          <v-simple-table class="members-table">
            <thead class="members-table-header">
              <tr>
                <th class="members-table-header-cell">ID</th>
                <th class="members-table-header-cell">名前</th>
                <th class="members-table-header-cell">メールアドレス</th>
                <th class="members-table-header-cell" style="width: 260px;"></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="member in organization.members" :key="member.id" class="members-table-row">
                <td class="members-table-cell">
                  <v-text-field
                    v-model="member.id"
                    :maxlength="8"
                    variant="outlined"
                    class="member-id-input"
                    readonly="true"
                    hide-details="auto"
                  ></v-text-field>
                </td>
                <td class="members-table-cell">
                  <v-text-field
                    v-model="member.name"
                    variant="outlined"
                    class="member-name-input"
                    :readonly="editingMember?.id !== member.id"
                    hide-details="auto"
                  ></v-text-field>
                </td>
                <td class="members-table-cell">
                  <v-text-field
                    v-model="member.email"
                    variant="outlined"
                    class="member-email-input"
                    :readonly="editingMember?.id !== member.id"
                    hide-details="auto"
                  ></v-text-field>
                </td>
                <td class="members-table-cell">
                  <v-simple-table class="action-table">
                    <tr>
                      <td v-if="editingMember?.id === member.id" class="action-cell">
                        <v-btn
                          class="save-button"
                          @click="handleUpdateMember(member)"
                        >
                          保存
                        </v-btn>
                      </td>
                      <td v-if="editingMember?.id === member.id" class="action-cell">
                        <v-btn
                          class="cancel-button"
                          @click="setEditingMember(null)"
                        >
                          キャンセル
                        </v-btn>
                      </td>
                      <td v-else class="action-cell">
                        <v-btn
                          class="edit-button"
                          @click="setEditingMember(member)"
                        >
                          編集
                        </v-btn>
                      </td>
                      <td v-if="editingMember?.id !== member.id" class="action-cell">
                        <v-btn
                          class="delete-button"
                          @click="handleDeleteMember(member.id)"
                        >
                          削除
                        </v-btn>
                      </td>
                    </tr>
                  </v-simple-table>
                </td>
              </tr>
            </tbody>
          </v-simple-table>
        </div>

        <div class="new-member-container">
          <div class="new-member-row">
            <v-text-field
              v-model="newMember.id"
              label="ID"
              :maxlength="8"
              variant="outlined"
              class="new-member-id-input"
            ></v-text-field>
            <v-text-field
              v-model="newMember.name"
              label="メンバー名"
              variant="outlined"
              class="new-member-name-input"
            ></v-text-field>
            <v-text-field
              v-model="newMember.email"
              label="メールアドレス"
              variant="outlined"
              class="new-member-email-input"
            ></v-text-field>
            <v-btn
              class="add-member-button"
              @click="handleAddMember"
            >
              メンバーを追加
            </v-btn>
          </div>
        </div>
      </v-card>
    </v-container>
  </v-app>
</template>

<script>
import { ref } from 'vue'

export default {
  name: 'OrganizationManagementSystem',
  setup() {
    const organization = ref({
      name: 'Example Organization',
      members: [
        { id: '0000001', name: '田中 太郎', email: 'tanaka.taro@example.com' },
        { id: '0000002', name: '鈴木 次郎', email: 'suzuki.jiro@example.com' },
        { id: '0000003', name: '佐藤 花子', email: 'sato.hanako@example.com' }
      ]
    })

    const newMember = ref({ id: '', name: '', email: '' })
    const editingMember = ref(null)

    const handleOrganizationNameChange = (e) => {
      organization.value.name = e.target.value
    }

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
        newMember.value = { id: '', name: '', email: '' }
      }
    }

    const setEditingMember = (member) => {
      editingMember.value = member ? { ...member } : null
    }

    const handleUpdateMember = (member) => {
      if (
        member.name.trim() !== '' &&
        member.email.trim() !== ''
      ) {
        organization.value.members = organization.value.members.map((m) =>
          m.id === member.id ? member : m
        )
        editingMember.value = null
      }
    }

    const handleDeleteMember = (memberId) => {
      organization.value.members = organization.value.members.filter((member) => member.id !== memberId)
    }

    return {
      organization,
      newMember,
      editingMember,
      handleOrganizationNameChange,
      handleAddMember,
      setEditingMember,
      handleUpdateMember,
      handleDeleteMember
    }
  }
}
</script>

<style scoped>
.organization-management-container {
  max-width: 960px;
  margin: 0 auto;
  padding: 2rem;
}

.organization-card {
  background-color: white;
  border-radius: 0.5rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  padding: 2rem;
}

.organization-name-input {
  font-size: 1.5rem;
  font-weight: bold;
}

.members-table-container {
  overflow-x: auto;
}

.members-table-header-cell {
  padding: .75rem;
  text-align: left;
}

.members-table-row {
  border-bottom: 1px solid #e0e0e0;
}

.members-table-cell {
  padding: .75rem;
  vertical-align: middle;
}

.members-table-cell input:read-only {
  border-style: none;
}

.new-member-container {
  margin-top: 1.5rem;
}

.new-member-row {
  display: flex;
  align-items: center;
}

.new-member-row .v-input {
  margin: .75rem;
  flex: none;
}

.member-id-input,
.new-member-id-input {
  width: 100px;
}

.member-name-input,
.new-member-name-input {
  width: 160px;
}

.member-email-input,
.new-member-email-input {
  width: 300px;
}

.save-button {
  background-color: #1a73e8 !important;
}

.cancel-button {
  background-color: #f2f2f2 !important;
  color: #4b5563 !important;
}

.edit-button {
  background-color: #f2f2f2 !important;
  color: #4b5563 !important;
}

.delete-button {
  background-color: #e53e3e !important;
}

.add-member-button {
  background-color: #1a73e8 !important;
}
</style>