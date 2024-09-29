<template>
  <v-dialog
    v-model="dialog"
    max-width="600"
  >
    <v-card rounded="lg">
      <v-card-title class="d-flex justify-space-between align-center">
        <div class="text-h5 text-medium-emphasis ps-2">
          {{ member.name }} さんの情報
        </div>
        <v-btn
          icon="mdi-close"
          variant="text"
          @click="closeDialog"
        ></v-btn>
      </v-card-title>
      <v-divider class="mb-4"></v-divider>
      <v-card-text>
        <div class="text-medium-emphasis mb-4">
          週次報告システムへようこそ。<br>
          あなたのお役に立てる機能をただいま開発中です。<br>
          <br>
          <v-textarea
            v-if="false"
            v-model="editableGoal"
            label="あなたの目標"
            rows="3"
            auto-grow
            outlined
            hide-details
          />
        </div>
      </v-card-text>
      <v-divider class="mt-2"></v-divider>
      <v-card-actions class="my-2 d-flex justify-end">
        <v-btn
          class="text-none"
          text="閉じる"
          @click="closeDialog"
        ></v-btn>
        <v-btn
          v-if="false"
          prepend-icon="mdi-check"
          class="text-none"
          text="保存"
          @click="saveAndCloseDialog"
        ></v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, inject, watch } from 'vue'
import { updateMemberGoal } from '../services/publicService'

const props = defineProps({
  member: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['update:member'])

const showNotification = inject('showNotification')
const dialog = ref(false)
const editableGoal = ref('')

watch(() => props.member.goal, (newGoal) => {
  editableGoal.value = newGoal
}, { immediate: true })

const openDialog = () => {
  editableGoal.value = props.member.goal
  dialog.value = true
}

const saveAndCloseDialog = async () => {
  try {
    await updateMemberGoal(props.member.memberUuid, editableGoal.value)
    // Update the member object with the new goal
    const updatedMember = { ...props.member, goal: editableGoal.value }
    emit('update:member', updatedMember)
    showNotification('情報を更新しました。')
    dialog.value = false
  } catch (error) {
    console.error('Goal update failed:', error)
    showNotification('情報の更新に失敗しました。', 'error')
  }
}

const closeDialog = () => {
  editableGoal.value = props.member.goal // Reset to the original value if not saved
  dialog.value = false
}

defineExpose({ openDialog })
</script>