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
      <v-card-text class="py-0">
        <div class="text-subtitle-1 mb-4">
          週次報告システムへようこそ。<br>
        </div>
        <div v-if="props.isAdviceEnabled" class="text-subtitle-2">
          AIアドバイザーからの回答を向上させるために、付加情報を指定できます。<br>
          <br>
          <v-text-field
            v-model="editableOccupation"
            label="あなたの職業"
            :rules="[v => !v || v.length <= 20 || '職業は20文字以内で入力してください']"
            maxlength="20"
            counter
            outlined
            hide-details="auto"
          />
          <v-textarea
            v-model="editableGoal"
            label="あなたの目標"
            :rules="[v => !v || v.length <= 50 || '目標は50文字以内で入力してください']"
            maxlength="50"
            counter
            rows="3"
            auto-grow
            outlined
            hide-details="auto"
          />
        </div>
        <div v-else class="text-subtitle-2">
          ここではAIアドバイザーからの回答を向上させるために付加情報を指定できます。<br>
          ・職業<br>
          ・目標<br>
          無料版ではこの機能を利用できません。
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
          v-if="props.isAdviceEnabled"
          prepend-icon="mdi-check"
          color="primary"
          class="text-none"
          text="保存"
          @click="saveAndCloseDialog"
        ></v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, inject } from 'vue'
import { updateMemberExtraInfo } from '../services/publicService'

const props = defineProps({
  member: {
    type: Object,
    required: true
  },
  isAdviceEnabled: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:member'])

const showNotification = inject('showNotification')
const dialog = ref(false)
const editableOccupation = ref('')
const editableGoal = ref('')

const openDialog = () => {
  editableOccupation.value = props.member.extraInfo?.occupation
  editableGoal.value = props.member.extraInfo?.goal
  dialog.value = true
}

const saveAndCloseDialog = async () => {
  try {
    const extraInfo = { occupation: editableOccupation.value, goal: editableGoal.value }
    await updateMemberExtraInfo(props.member.memberUuid, extraInfo)
    const updatedMember = { ...props.member, extraInfo }
    emit('update:member', updatedMember)
    showNotification('情報を更新しました。')
    dialog.value = false
  } catch (error) {
    console.error('ExtraInfo update failed:', error)
    showNotification('情報の更新に失敗しました。', 'error')
  }
}

const closeDialog = () => {
  editableGoal.value = props.member.goal // Reset to the original value if not saved
  dialog.value = false
}

defineExpose({ openDialog })
</script>