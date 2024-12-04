<template>
  <v-container class="report-settings-container">
    <v-row dense class="pb-4">
      <v-col>
        <h3>
          <v-icon size="large" class="mr-1">mdi-calendar-clock</v-icon>
          週次報告設定
        </h3>
      </v-col>
    </v-row>

    <v-card 
      v-if="loading"
      class="pa-6 rounded-lg"
      outlined
    >
      <v-skeleton-loader
        type="text, chip@2, ossein, text, paragraph, button"
      />
    </v-card>

    <v-tabs
      v-if="!loading"
      v-model="activeTab"
      class="mb-4"
    >
      <v-tab value="request" class="text-body-1">報告依頼設定</v-tab>
      <v-tab value="notification" class="text-body-1">通知設定</v-tab>
      <v-tab value="advisor" class="text-body-1">アドバイザー設定</v-tab>
    </v-tabs>

    <v-card-text v-if="!loading" class="pa-0">
      <v-tabs-window 
        v-model="activeTab" 
        class="elevation-4"
      >
        <v-tabs-window-item value="request">
          <v-card class="setting-card rounded-lg" outlined>
            <v-card-text class="px-6 pt-6">
              <v-form ref="form" v-model="isFormValid" @submit.prevent="handleSubmit">
                <v-row>
                  <v-col cols="12" md="6">
                    <v-text-field
                      v-model="reportSettings.sender"
                      label="送信元メールアドレス"
                      outlined
                      dense
                      hide-details="auto"
                      :rules="emailRules"
                      :color="emailVerificationStatus === 'Success' ? 'success' : ''"
                      :error="emailVerificationStatus === 'Failed'"
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
                        v-if="isValidEmail(reportSettings.sender) && emailVerificationStatus !== 'Success' && emailVerificationStatus !== 'Checking'"
                        color="secondary"
                        small
                        prepend-icon="mdi-card-account-mail"
                        :loading="verifyingEmail"
                        @click="verifyEmail(reportSettings.sender)"
                      >
                        メールアドレスを検証する
                      </v-btn>
                    </div>
                  </v-col>
                  <v-col cols="12" md="6">
                    <v-text-field
                      v-model="reportSettings.senderName"
                      label="送信者名"
                      outlined
                      dense
                      hide-details="auto"
                      :rules="senderNameRules"
                    >
                    </v-text-field>
                  </v-col>
                </v-row>

                <v-card outlined class="mt-8">
                  <v-card-title>自動送信設定</v-card-title>
                  <v-card-text>
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
                          <v-radio-group v-model="reportSettings.reportWeek" row dense hide-details>
                            <v-radio :label="option.text" :value="option.value"></v-radio>
                          </v-radio-group>
                        </span>
                      </v-col>
                    </v-row>

                    <v-row>
                      <v-col cols="12" class="py-1">
                        <div class="d-flex align-center justify-start">
                          <div class="d-flex align-center">
                            <v-icon
                              :color="reportSettings.requestEnabled ? 'success' : 'grey'"
                              class="mr-2"
                              size="large"
                            >
                              {{ reportSettings.requestEnabled ? 'mdi-timer-outline' : 'mdi-timer-off-outline' }}
                            </v-icon>
                            <span class="text-subtitle-1">
                              <span class="d-none d-sm-inline">報告依頼の自動送信は</span>現在
                              <strong>{{ reportSettings.requestEnabled ? '有効' : '無効' }}</strong>
                              です
                            </span>
                          </div>
                          <span class="mx-3"></span>
                          <v-switch
                            v-model="reportSettings.requestEnabled"
                            color="primary"
                            class="mr-3"
                            density="compact"
                            inset
                            hide-details
                          ></v-switch>
                        </div>
                      </v-col>
                    </v-row>

                    <v-row>
                      <v-col cols="12" sm="4">
                        <v-select
                          v-model="reportSettings.requestDayOfWeek"
                          :items="daysOfWeek"
                          label="送信曜日"
                          item-title="text"
                          item-value="value"
                          outlined
                          dense
                          hide-details="auto"
                          :disabled="!reportSettings.requestEnabled"
                        ></v-select>
                      </v-col>
                      <v-col cols="12" sm="4">
                        <v-select
                          v-model="reportSettings.requestTime"
                          :items="hours"
                          label="送信時間"
                          item-title="text"
                          item-value="value"
                          outlined
                          dense
                          hide-details="auto"
                          :disabled="!reportSettings.requestEnabled"
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

                <v-row class="mt-2">
                  <v-col cols="12" class="d-flex justify-end">
                    <v-btn
                      color="primary"
                      type="submit"
                      :loading="loading"
                      :disabled="!isFormValid || !isFormChanged"
                    >
                      <v-icon class="mr-1">mdi-check</v-icon>
                      更新する
                    </v-btn>
                  </v-col>
                </v-row>
              </v-form>
            </v-card-text>
          </v-card>
        </v-tabs-window-item>

        <v-tabs-window-item value="notification" eager>
          <v-card class="setting-card rounded-lg">
            <v-card-text class="px-6">
              <template v-if="currentPlan.adminFeatures.notifications">
                <p class="text-body-1 my-2">
                  通知を有効にすると週次報告が送信されたときに通知を受け取ることができます。
                </p>
                <div>
                  <v-switch
                    v-model="isMailSubscribed"
                    color="primary"
                    hide-details
                    inset
                    @click="toggleMailNotification"
                  >
                    <template #prepend>
                      <v-icon
                        :color="isMailSubscribed ? 'success' : 'grey'"
                        class="mr-1"
                        size="large"
                      >
                        {{ isMailSubscribed ? 'mdi-email-outline' : 'mdi-email-off-outline' }}
                      </v-icon>
                      {{ isMailSubscribed ? 'メール通知: 有効' : 'メール通知: 無効' }}
                    </template>
                  </v-switch>
                </div>

                <PushNortification></PushNortification>
              </template>
              <template v-else>
                <v-alert
                  type="info"
                  variant="tonal"
                  class="mt-4 rounded-lg"
                >
                  <div class="d-flex align-center gap-4">
                    <span>通知機能はプロプラン以上でご利用いただけます。</span>
                    <v-spacer></v-spacer>
                    <v-btn
                      v-if="!isMobile"
                      color="primary"
                      @click="router.push({ name: 'Billing' })"
                    >
                      プランをアップグレード
                    </v-btn>
                  </div>
                </v-alert>
              </template>
            </v-card-text>
          </v-card>
        </v-tabs-window-item>

        <v-tabs-window-item value="advisor">
          <v-card class="setting-card rounded-lg">
            <v-card-text class="px-6">
              <template v-if="currentPlan.adminFeatures.advisorSettings">
                <p class="mt-2 mb-4">
                  メンバーは選択したアドバイザーから週次報告に対するアドバイスを受け取ることができます。
                </p>
                <p 
                  v-if="!hasSelectedAdvisor"
                  class="text-caption mb-3 text-warning" 
                >
                  <v-icon color="warning" size="small" class="mr-1">mdi-alert-circle</v-icon>
                  少なくとも1つのアドバイザーを選択してください
                </p>
                <v-row>
                  <v-col 
                    v-for="(advisor, key) in availableAdvisors"
                    :key="key"
                    cols="12"
                    sm="6"
                    md="3"
                  >
                    <v-card
                      v-tooltip:bottom="advisor.description"
                      variant="outlined"
                      :class="['advisor-card', { 'advisor-selected': selectedAdvisors.includes(key) }]"
                      :elevation="selectedAdvisors.includes(key) ? 4 : 0"
                      @click="toggleAdvisor(key)"
                    >
                      <v-img
                        :src="advisor.image"
                        height="120"
                        fill
                        class="advisor-image mx-6 mt-4"
                      ></v-img>
                      <v-card-item>
                        <v-card-title class="text-subtitle-2 text-center">
                          {{ advisor.title }}
                        </v-card-title>
                      </v-card-item>
                    </v-card>
                  </v-col>
                </v-row>
                <div class="d-flex justify-end mt-4">
                  <v-btn
                    color="primary"
                    :loading="isSaving"
                    :disabled="!hasSelectedAdvisor || !isAdvisorSettingsChanged"
                    @click="saveAdvisorSettings"
                  >
                    <v-icon class="mr-1">mdi-check</v-icon>
                    更新する
                  </v-btn>
                </div>
              </template>
              <template v-else>
                <v-alert
                  type="info"
                  variant="tonal"
                  class="mt-4 rounded-lg"
                >
                  <div class="d-flex align-center gap-4">
                    <span>アドバイザー設定はプロプラン以上でご利用いただけます。</span>
                    <v-spacer></v-spacer>
                    <v-btn
                      v-if="!isMobile"
                      color="primary"
                      @click="router.push({ name: 'Billing' })"
                    >
                      プランをアップグレード
                    </v-btn>
                  </div>
                </v-alert>
              </template>
            </v-card-text>
          </v-card>
        </v-tabs-window-item>
      </v-tabs-window>
    </v-card-text>
  </v-container>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, inject } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import PushNortification from '../components/PushNortification.vue'
import { getOrganization, updateOrganization, updateOrganizationFeatures } from '../services/organizationService'
import { checkEmailVerification, verifyEmailAddress } from '../services/sesService'
import { advisorRoles, defaultAdvisors } from '../services/bedrockService'
import { isValidEmail } from '../utils/string-utils'
import { getCurrentPlan } from '../config/plans'
import { useResponsive } from '../composables/useResponsive'

const router = useRouter()
const store = useStore()
const showNotification = inject('showNotification')
const showError = inject('showError')

const form = ref(null)
const loading = ref(false)
const isFormValid = ref(false)
const activeTab = ref('request')

const currentPlan = computed(() => getCurrentPlan())
const organization = ref(null)
const organizationId = store.getters['auth/organizationId']
const { isMobile } = useResponsive()

const useEmailVerification = () => {
  const status = ref('Pending')
  const verifying = ref(false)

  const statusColor = computed(() => ({
    Success: 'success', Failed: 'error', Pending: 'grey', Checking: 'grey', Error: 'error'
  }[status.value] || 'grey'))

  const statusIcon = computed(() => ({
    Success: 'mdi-check-circle', Failed: 'mdi-alert-circle', Pending: 'mdi-progress-clock',
    Checking: 'mdi-progress-clock', Error: 'mdi-alert'
  }[status.value] || 'mdi-progress-clock'))

  const statusText = computed(() => ({
    Success: '検証済み', Failed: '未検証', Pending: '検証中', Checking: '検証中', Error: 'エラー'
  }[status.value] || '検証中'))

  const check = async (email) => {
    if (!email || !isValidEmail(email)) {
      status.value = 'Failed'
      return
    }
    try {
      status.value = 'Checking'
      const result = await checkEmailVerification(email)
      status.value = result.status
      // 直接の check 呼び出し時のみ通知を表示
      if (result.status === 'Pending' && !verifying.value) {
        showNotification('メールアドレスの検証が保留中です。メールボックスを確認してください。', 'info')
      }
    } catch (error) {
      status.value = 'Error'
      showError('メールアドレスの検証状態の確認中にエラーが発生しました。', error)
    }
  }

  const verify = async (email) => {
    if (!email || !isValidEmail(email)) {
      showError('有効なメールアドレスを入力してください。')
      return
    }
    verifying.value = true
    try {
      await verifyEmailAddress(email)
      showNotification('検証メールを送信しました。メールを確認して検証を完了してください。', 'info')
      await check(email) // check メソッドを呼び出すが、verifying フラグにより通知は表示されない
    } catch (error) {
      showError('メールアドレスの検証に失敗しました。', error)
    } finally {
      verifying.value = false
    }
  }

  return { status, statusColor, statusIcon, statusText, check, verify, verifying }
}

const {
  status: emailVerificationStatus,
  statusColor: emailVerificationStatusColor,
  statusIcon: emailVerificationStatusIcon,
  statusText: emailVerificationStatusText,
  check: checkEmailVerificationStatus,
  verify: verifyEmail,
  verifying: verifyingEmail,
} = useEmailVerification()

const reportSettings = reactive({
  requestEnabled: true,
  sender: '',
  senderName: '',
  requestDayOfWeek: 'monday',
  requestTime: '06:00',
  reportWeek: -1,
})

const originalSettings = ref(null)

const isFormChanged = computed(() =>
  originalSettings.value && JSON.stringify(reportSettings) !== JSON.stringify(originalSettings.value)
)

const emailRules = [
  v => !!v || 'メールアドレスは必須です',
  v => isValidEmail(v) || '有効なメールアドレスを入力してください',
]

const senderNameRules = [
  v => !!v || '送信者名は必須です',
  v => (v && v.length <= 50) || '送信者名は50文字以内で入力してください'
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

const hours = computed(() =>
  Array.from({ length: 24 }, (_, i) => {
    const time = `${i.toString().padStart(2, '0')}:00`
    return { text: time, value: time }
  })
)

const reportWeekOptions = [
  { text: '前週', value: -1 },
  { text: '当週', value: 0 },
]

watch(() => reportSettings.sender, (newValue, oldValue) => {
  if (newValue !== oldValue) {
    if (isValidEmail(newValue)) {
      const timeoutId = setTimeout(() => checkEmailVerificationStatus(newValue), 500)
      return () => clearTimeout(timeoutId)
    } else {
      emailVerificationStatus.value = 'Failed'
    }
  }
})

const handleSubmit = async () => {
  if (!isFormValid.value || !isFormChanged.value) return
  
  await checkEmailVerificationStatus(reportSettings.sender)
  if (emailVerificationStatus.value !== 'Success') {
    showError('送信元メールアドレスが検証されていません。設定を保存できません。')
    return
  }
  
  try {
    const org = { ...organization.value, ...reportSettings }
    await updateOrganization(org)
    showNotification('報告依頼設定を更新しました')
    originalSettings.value = JSON.parse(JSON.stringify(reportSettings))
  } catch (error) {
    showError('報告依頼設定の保存に失敗しました', error)
  }
}

const isMailSubscribed = ref(false)

const toggleMailNotification = async () => {
  if (!currentPlan.value.adminFeatures.notifications) {
    showError('この機能はプロプラン以上でご利用いただけます。')
    return
  }
  try {
    const newValue = !isMailSubscribed.value
    await updateOrganizationFeatures(organizationId, {
      mailSubscribed: newValue
    })
    isMailSubscribed.value = newValue
  } catch (error) {
    showError('メール通知設定の更新に失敗しました', error)
    // エラー時は元の値に戻す
    isMailSubscribed.value = !isMailSubscribed.value
  }
}

// アドバイザー設定用の状態変数
const selectedAdvisors = ref([])
const originalAdvisors = ref([])
const isSaving = ref(false)

// アドバイザー設定が変更されたかどうかをチェック
const isAdvisorSettingsChanged = computed(() => {
  const currentAdvisors = [...selectedAdvisors.value].sort()
  const originalAdvisorsList = [...originalAdvisors.value].sort()
  return JSON.stringify(currentAdvisors) !== JSON.stringify(originalAdvisorsList)
})

// アドバイザーフィルタリング用の computed property を追加
const availableAdvisors = computed(() => {
  if (currentPlan.value.systemFeatures.weeklyReportAdvice) {
    return advisorRoles
  }
  return Object.fromEntries(
    Object.entries(advisorRoles).filter(([key]) => defaultAdvisors.includes(key))
  )
})

// アドバイザー選択のバリデーション
const hasSelectedAdvisor = computed(() => selectedAdvisors.value.length > 0)

// アドバイザー設定の選択切り替え
const toggleAdvisor = (advisorKey) => {
  if (!currentPlan.value.systemFeatures.weeklyReportAdvice) {
    showError('この機能はプロプラン以上でご利用いただけます。')
    return
  }
  const index = selectedAdvisors.value.indexOf(advisorKey)
  if (index === -1) {
    selectedAdvisors.value.push(advisorKey)
  } else {
    selectedAdvisors.value.splice(index, 1)
  }
}

// アドバイザー設定を保存
const saveAdvisorSettings = async () => {
  if (!hasSelectedAdvisor.value) {
    showError('少なくとも1つのアドバイザーを選択してください')
    return
  }

  isSaving.value = true
  try {
    const organizationId = store.getters['auth/organizationId']
    await updateOrganizationFeatures(organizationId, { advisors: selectedAdvisors.value })

    showNotification('アドバイザー設定を保存しました')
  } catch (error) {
    showError('アドバイザー設定の保存に失敗しました', error)
  } finally {
    isSaving.value = false
  }
}

onMounted(async () => {
  loading.value = true
  try {
    const result = await getOrganization(organizationId)
    organization.value = result
    if (result && Object.keys(result).length > 0) {
      Object.assign(reportSettings, {
        sender: result.sender || '',
        senderName: result.senderName || '',
        requestEnabled: result.requestEnabled ?? false,
        requestTime: result.requestTime || '06:00',
        requestDayOfWeek: result.requestDayOfWeek || 'monday',
        reportWeek: result.reportWeek || -1,
      })
      originalSettings.value = JSON.parse(JSON.stringify(reportSettings))
      await checkEmailVerificationStatus(reportSettings.sender)

      selectedAdvisors.value = result.features?.advisors || defaultAdvisors
      originalAdvisors.value = [...selectedAdvisors.value]

      // メール通知設定の初期化を追加
      isMailSubscribed.value = result.features?.mailSubscribed ?? false
    }
  } catch (error) {
    showError('報告依頼設定の取得に失敗しました', error)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.report-settings-container {
  max-width: 960px;
}

.setting-card {
  min-height: 500px;
}

.v-radio-group {
  display: flex;
  align-items: center;
}

.v-radio {
  margin-right: 0;
}

.advisor-card {
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid rgba(var(--v-border-color), 0.3);
  position: relative;
  border-radius: 12px;
}

.advisor-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  background-color: rgba(var(--v-theme-primary), 0.1);
}

.advisor-selected {
  border: 1px solid rgb(var(--v-theme-primary));
  background-color: rgba(var(--v-theme-primary), 0.1);
}

.advisor-selected::after {
  content: '✓';
  position: absolute;
  top: 8px;
  right: 8px;
  background-color: rgb(var(--v-theme-primary));
  color: white;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: bold;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  z-index: 1;
}

.advisor-image {
  opacity: 0.9;
  transition: opacity 0.3s ease;
}

.advisor-card:hover .advisor-image {
  opacity: 1;
}

.text-warning {
  color: rgb(var(--v-theme-warning));
}

.v-alert {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.v-alert :deep(.v-alert__content) {
  width: 100%;
}
</style>