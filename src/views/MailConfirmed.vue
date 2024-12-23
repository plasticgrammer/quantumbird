<template>
  <v-container v-if="!loading">
    <v-row dense class="pb-3">
      <v-col>
        <v-card 
          class="mt-6 mx-auto pa-2 text-center rounded-lg"
          max-width="640"
        >
          <v-card-title class="text-h5">
            メールアドレスを確認済みとしました
          </v-card-title>
          <v-card-text>
            <p class="text-body-1 text-blue-accent-4">
              {{ email }}
            </p>
            <v-img
              src="@/assets/images/advisor_mental.png"
              max-width="200"
              class="mx-auto mt-0 mb-5"
              :aspect-ratio="1"
            ></v-img>
            <p class="text-body-1">
              報告要求のメールが配信されるまでお待ちください。
            </p>
          </v-card-text>
          <v-card-actions v-if="canClose" class="justify-center">
            <v-btn color="error" prepend-icon="mdi-close" variant="outlined" @click="handleClose">
              閉じる
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, inject, onMounted } from 'vue'
import { verifyEmail } from '../services/memberService'

const props = defineProps({
  memberUuid: {
    type: String,
    required: true
  }
})

const loading = ref(false)
const email = ref('')
const showError = inject('showError')
const canClose = ref(false)

const handleClose = () => {
  window.close()
}

const checkCloseAvailability = () => {
  try {
    canClose.value = window.opener !== null && !window.opener.closed
  } catch (e) {
    canClose.value = false
  }
}

onMounted(async () => {
  loading.value = true
  try {
    const result = await verifyEmail(props.memberUuid)
    email.value = result.email
    loading.value = false
    checkCloseAvailability()
  } catch (error) {
    showError('メール確認済み更新に失敗しました', error)
  }
})
</script>