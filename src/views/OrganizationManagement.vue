<template>
  <v-container class="organization-management-container">
    <v-card 
      class="organization-card"
      elevation="4"
      outlined
    >
      <v-form>
        <v-text-field
          v-model="organization.name"
          label="組織名"
          outlined
          dense
          class="organization-name-input"
          @input="handleOrganizationNameChange"
        ></v-text-field>
      </v-form>

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
                variant=""
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
                :variant="editingMember?.id !== member.id ? '' : 'filled'"
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
                :variant="editingMember?.id !== member.id ? '' : 'filled'"
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
            <td>
            </td>
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

      <v-btn color="success" type="submit" class="mt-4">
        <v-icon class="mr-1" left>mdi-check</v-icon>
        更新する
      </v-btn>
      <span class="px-3"></span>
      <v-btn color="grey lighten-1" type="submit" class="mt-4">
        <v-icon class="mr-1" left>mdi-cancel</v-icon>
        更新しない
      </v-btn>

    </v-card>
  </v-container>
</template>

<script>
import { ref } from 'vue'

export default {
  name: 'OrganizationManagement',
  setup() {
    const organization = ref({
      name: 'ジェイエスピー 開発３グループ',
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
</style>