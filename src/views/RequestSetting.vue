<template>
  <v-container class="request-settings-container">
    <v-row dense class="pb-4">
      <v-col>
        <h3>
          <v-icon size="large" class="mr-1">mdi-mail</v-icon>
          報告依頼設定
        </h3>
      </v-col>
    </v-row>

    <v-card class="request-settings-card pt-5" outlined>
      <v-skeleton-loader
        v-if="loading"
        type="text, chip@2, ossein, text, paragraph, button"
      />

      <v-form v-else ref="form" v-model="isFormValid" @submit.prevent="handleSubmit">
        <v-row>
          <v-col cols="12" md="6">
            <v-text-field
              v-model="requestSettings.sender"
              label="送信元メールアドレス"
              outlined
              dense
              hide-details
              :rules="emailRules"
              :color="emailVerificationStatus === 'Success' ? 'success' : ''"
              :error="emailVerificationStatus === 'Failed'"
              @input="debouncedCheckEmailVerification"
            >
              <template #append>
                <v-icon 
                  v-tooltip:top="emailVerificationStatusText"
                  :color="emailVerificationStatusColor"
                >
                  {{ emailVerificationStatusIcon }}
                </v-icon>
              </template>
            </v-text-field>
          </v-col>
          <v-col cols="12" md="6">
            <div class="d-flex align-center mt-2">
              <v-btn
                v-if="emailVerificationStatus !== 'Success' && emailVerificationStatus !== 'Checking'"
                color="success"
                small
                prepend-icon="mdi-card-account-mail"
                :loading="verifyingEmail"
                @click="verifyEmail"
              >
                メールアドレスを検証する
              </v-btn>
            </div>
          </v-col>
          <v-col cols="12" md="6">
            <v-text-field
              v-model="requestSettings.senderName"
              label="送信者名"
              outlined
              dense
              hide-details
            >
            </v-text-field>
          </v-col>
        </v-row>

        <v-divider class="mt-5 mb-3"></v-divider>

        <v-row>
          <v-col cols="12" md="2" class="pl-5 d-flex align-center">
            <span class="text-body-1">報告対象週</span>
          </v-col>
          <v-col cols="12" md="10" class="d-flex justify-start align-center">
            <span
              v-for="option in reportWeekOptions"
              :key="option.value"
              class="mr-4"
            >
              <v-radio-group v-model="requestSettings.reportWeek" row dense hide-details>
                <v-radio :label="option.text" :value="option.value"></v-radio>
              </v-radio-group>
            </span>
          </v-col>
        </v-row>

        <v-card outlined class="mt-4">
          <v-card-title>自動送信設定</v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="12" class="py-1">
                <div class="d-flex align-center justify-start">
                  <div class="d-flex align-center">
                    <v-icon
                      :color="requestSettings.requestEnabled ? 'success' : 'error'"
                      class="mr-2"
                    >
                      {{ requestSettings.requestEnabled ? 'mdi-check-circle' : 'mdi-close-circle' }}
                    </v-icon>
                    <span class="text-subtitle-1">
                      <span class="d-none d-sm-inline">報告依頼の自動送信は</span>現在
                      <strong>{{ requestSettings.requestEnabled ? '有効' : '無効' }}</strong>
                      です
                    </span>
                  </div>
                  <span class="mx-3"></span>
                  <v-switch
                    v-model="requestSettings.requestEnabled"
                    color="primary"
                    hide-details="auto"
                    class="mr-3"
                    inset
                  ></v-switch>
                </div>
              </v-col>
            </v-row>

            <v-row>
              <v-col cols="12" sm="4">
                <v-select
                  v-model="requestSettings.requestDayOfWeek"
                  :items="daysOfWeek"
                  label="送信曜日"
                  item-title="text"
                  item-value="value"
                  outlined
                  dense
                  hide-details="auto"
                ></v-select>
              </v-col>
              <v-col cols="12" sm="4">
                <v-select
                  v-model="requestSettings.requestTime"
                  :items="hours"
                  label="送信時間"
                  item-title="text"
                  item-value="value"
                  outlined
                  dense
                  hide-details="auto"
                  :rules="[v => v !== null || '時間を選択してください']"
                >
                  <template #prepend-inner>
                    <v-icon>mdi-clock-outline</v-icon>
                  </template>
                </v-select>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>

        <v-row class="mt-4">
          <v-col>
            <v-btn
              color="primary"
              type="submit"
              :loading="loading"
              :disabled="!isFormValid || !isFormChanged"
            >
              <v-icon class="mr-1" left> mdi-check </v-icon>
              更新する
            </v-btn>
          </v-col>
        </v-row>
      </v-form>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, inject } from 'vue'
import { useStore } from 'vuex'
import { getOrganization, updateOrganization } from '../services/organizationService'
import { checkEmailVerification, verifyEmailAddress } from '../services/sesService'

const store = useStore()
const organizationId = computed(() => store.getters['user/organizationId'])

const form = ref(null)
const loading = ref(false)
const isFormValid = ref(false)
const organization = ref(null)
const showNotification = inject('showNotification')

const requestSettings = reactive({
  requestEnabled: true,
  sender: '',
  requestDayOfWeek: 'monday',
  requestTime: 6,
  reportWeek: -1,
})

const originalSettings = ref(null)

const isFormChanged = computed(() => {
  if (!originalSettings.value) return false
  return JSON.stringify(requestSettings) !== JSON.stringify(originalSettings.value)
})

const emailRules = [
  v => !!v || 'メールアドレスは必須です',
  v => /.+@.+\..+/.test(v) || '有効なメールアドレスを入力してください',
]

const daysOfWeek = [
  { text: '月曜日', value: 'monday' },
  { text: '火曜日', value: 'tuesday' },
  { text: '水曜日', value: 'wednesday' },
  { text: '木曜日', value: 'thursday' },
  { text: '金曜日', value: 'friday' },
  { text: '土曜日', value: 'saturday' },
  { text: '日曜日', value: 'sunday' },
]

const hours = ref(
  Array.from({ length: 24 }, (_, i) => {
    const timeString = `${i.toString().padStart(2, '0')}:00`
    return {
      text: timeString,
      value: timeString,
    }
  })
)

const reportWeekOptions = [
  { text: '前週', value: -1 },
  { text: '当週', value: 0 },
]
const emailVerificationStatus = ref('Pending')
const emailVerificationTimeout = ref(null)
const verifyingEmail = ref(false)

const emailVerificationStatusColor = computed(() => {
  switch (emailVerificationStatus.value) {
  case 'Success':
    return 'success'
  case 'Failed':
    return 'error'
  default:
    return 'grey'
  }
})

const emailVerificationStatusIcon = computed(() => {
  switch (emailVerificationStatus.value) {
  case 'Success':
    return 'mdi-check-circle'
  case 'Failed':
    return 'mdi-alert-circle'
  default:
    return 'mdi-progress-clock'
  }
})

const emailVerificationStatusText = computed(() => {
  switch (emailVerificationStatus.value) {
  case 'Success':
    return '検証済み'
  case 'Failed':
    return '未検証'
  default:
    return '検証中'
  }
})

const debouncedCheckEmailVerification = () => {
  if (emailVerificationTimeout.value) {
    clearTimeout(emailVerificationTimeout.value)
  }
  emailVerificationTimeout.value = setTimeout(async () => {
    await checkEmailVerificationStatus()
  }, 500)
}
const checkEmailVerificationStatus = async () => {
  if (!requestSettings.sender) {
    emailVerificationStatus.value = 'Pending'
    return
  }

  try {
    emailVerificationStatus.value = 'Checking'
    const result = await checkEmailVerification(requestSettings.sender)
    
    switch (result.status) {
    case 'Success':
      emailVerificationStatus.value = 'Success'
      break
    case 'Pending':
      emailVerificationStatus.value = 'Pending'
      showNotification('メールアドレスの検証が保留中です。メールボックスを確認してください。', 'info')
      break
    case 'Failed':
      emailVerificationStatus.value = 'Failed'
      //showNotification('メールアドレスの検証に失敗しました。', 'error')
      break
    default:
      emailVerificationStatus.value = 'Error'
      showNotification('メールアドレスの検証状態の確認中にエラーが発生しました。', 'error')
    }
  } catch (error) {
    console.error('Error checking email verification:', error)
    emailVerificationStatus.value = 'Error'
    showNotification('メールアドレスの検証状態の確認中にエラーが発生しました。', 'error')
  }
}

const verifyEmail = async () => {
  if (!requestSettings.sender) {
    showNotification('メールアドレスを入力してください。', 'error')
    return
  }

  verifyingEmail.value = true
  try {
    await verifyEmailAddress(requestSettings.sender)
    showNotification('検証メールを送信しました。メールを確認して検証を完了してください。', 'success')
    await checkEmailVerificationStatus()
  } catch (error) {
    console.error('Error verifying email:', error)
    showNotification('メールアドレスの検証に失敗しました。', 'error')
  } finally {
    verifyingEmail.value = false
  }
}

const handleSubmit = async () => {
  if (!isFormValid.value || !isFormChanged.value) return

  // Check email verification before submitting
  await checkEmailVerificationStatus()
  if (emailVerificationStatus.value !== 'Success') {
    showNotification('送信元メールアドレスが検証されていません。設定を保存できません。', 'error')
    return
  }

  try {
    const org = {
      ...organization.value,
      ...requestSettings,
    }
    await updateOrganization(org)
    showNotification('報告依頼設定を更新しました')
    console.log('Request settings updated:', requestSettings)
    originalSettings.value = JSON.parse(JSON.stringify(requestSettings))
  } catch (error) {
    showNotification('報告依頼設定の保存に失敗しました', error)
  }
}

onMounted(async () => {
  loading.value = true
  try {
    const result = await getOrganization(organizationId.value)
    organization.value = result
    if (result && Object.keys(result).length > 0) {
      Object.assign(requestSettings, {
        sender: result.sender || '',
        requestEnabled: result.requestEnabled ?? false,
        requestTime: result.requestTime || '06:00',
        requestDayOfWeek: result.requestDayOfWeek || 'monday',
        reportWeek: result.reportWeek || -1,
      })
      originalSettings.value = JSON.parse(JSON.stringify(requestSettings))
      
      // Check email verification status on mount
      await checkEmailVerificationStatus()
    }
  } catch (error) {
    showNotification('報告依頼設定の取得に失敗しました', error)
  } finally {
    loading.value = false
  }
})

// Clean up the timeout when the component is unmounted
onUnmounted(() => {
  if (emailVerificationTimeout.value) {
    clearTimeout(emailVerificationTimeout.value)
  }
})
</script>

<style scoped>
.request-settings-container {
  max-width: 960px;
}

.request-settings-card {
  background-color: white;
  border-radius: 0.5rem;
  padding: 0.5em 1.5em 1em;
  position: relative;
}

.v-radio-group {
  display: flex;
  align-items: center;
}

.v-radio {
  margin-right: 0;
}
</style>