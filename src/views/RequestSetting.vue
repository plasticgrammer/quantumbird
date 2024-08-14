<template>
  <v-container class="request-settings-container">
    <v-row dense class="pb-4">
      <v-col>
        <h3>
          <v-icon size="large" class="mr-1"> mdi-bell-ring </v-icon>
          報告依頼設定
        </h3>
      </v-col>
    </v-row>

    <v-card class="request-settings-card pt-5" outlined>
      <v-form ref="form" v-model="isFormValid" @submit.prevent="handleSubmit">
        <v-row>
          <v-col cols="12">
            <v-text-field
              v-model="requestSettings.sender"
              label="送信元メールアドレス"
              outlined
              dense
              hide-details="auto"
              :rules="emailRules"
            ></v-text-field>
          </v-col>
        </v-row>

        <v-row>
          <v-col cols="2" class="pl-5 d-flex align-center">
            <span class="text-body-1">報告対象週</span>
          </v-col>
          <v-col cols="10" class="d-flex justify-start align-center">
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
          <v-card-title>報告依頼 - 自動送信設定</v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="12">
                <div class="d-flex align-center justify-start">
                  <div class="d-flex align-center">
                    <v-icon
                      :color="requestSettings.isEnabled ? 'success' : 'error'"
                      class="mr-2"
                    >
                      {{ requestSettings.isEnabled ? 'mdi-check-circle' : 'mdi-close-circle' }}
                    </v-icon>
                    <span class="text-subtitle-1">
                      報告依頼の自動送信は現在
                      <strong>{{ requestSettings.isEnabled ? '有効' : '無効' }}</strong>
                      です
                    </span>
                  </div>
                  <span class="mx-3"></span>
                  <v-switch
                    v-model="requestSettings.isEnabled"
                    color="primary"
                    hide-details="auto"
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
              設定を保存する
            </v-btn>
          </v-col>
          <v-col>
            <v-btn
              color="secondary"
              :loading="manualExecutionLoading"
              :disabled="!requestSettings.isEnabled"
              @click="handleManualExecution"
            >
              <v-icon class="mr-1" left> mdi-play </v-icon>
              手動実行
            </v-btn>
          </v-col>
        </v-row>
      </v-form>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import {
  getOrganization,
  updateOrganization,
  executeManualRequest,
} from '../services/organizationService'

const store = useStore()
const organizationId = computed(() => store.getters['user/organizationId'])

const form = ref(null)
const loading = ref(false)
const manualExecutionLoading = ref(false)
const isFormValid = ref(false)

const requestSettings = reactive({
  isEnabled: true,
  sender: '',
  requestDayOfWeek: 'monday',
  requestTime: null,
  reportWeek: 'current',
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
  Array.from({ length: 24 }, (_, i) => ({
    text: `${i.toString().padStart(2, '0')}:00`,
    value: i,
  }))
)

const reportWeekOptions = [
  { text: '当週', value: 'current' },
  { text: '前週', value: 'previous' },
]

const handleSubmit = async () => {
  if (!isFormValid.value || !isFormChanged.value) return

  try {
    loading.value = true
    await updateOrganization({
      ...organizationId.value,
      ...requestSettings,
    })
    showNotification('報告依頼設定を更新しました')
    console.log('Request settings updated:', requestSettings)
    originalSettings.value = JSON.parse(JSON.stringify(requestSettings))
  } catch (error) {
    showNotification('報告依頼設定の保存に失敗しました', error)
  } finally {
    loading.value = false
  }
}

const handleManualExecution = async () => {
  try {
    manualExecutionLoading.value = true
    await executeManualRequest(organizationId.value)
    showNotification('報告依頼を手動で実行しました')
  } catch (error) {
    showNotification('報告依頼の手動実行に失敗しました', error)
  } finally {
    manualExecutionLoading.value = false
  }
}

onMounted(async () => {
  loading.value = true
  try {
    const result = await getOrganization(organizationId.value)
    if (result && Object.keys(result).length > 0) {
      Object.assign(requestSettings, {
        isEnabled: result.isEnabled ?? false,
        sender: result.sender || '',
        requestTime: result.requestTime !== undefined ? Number(result.requestTime) : null,
        requestDayOfWeek: result.requestDayOfWeek || 'monday',
        reportWeek: result.reportWeek || 'current',
      })
      originalSettings.value = JSON.parse(JSON.stringify(requestSettings))
    }
  } catch (error) {
    showNotification('報告依頼設定の取得に失敗しました', error)
  } finally {
    loading.value = false
  }
})

// 通知用のユーティリティ関数（実際の実装に置き換えてください）
const showNotification = (message, error) => {
  console.log(message, error)
  // ここに通知ロジックを実装してください
}
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