<template>
  <v-container class="request-settings-container">
    <v-row dense class="pb-4">
      <v-col>
        <h3>
          <v-icon size="large" class="mr-1">
            mdi-bell-ring
          </v-icon>
          報告依頼設定
        </h3>
      </v-col>
    </v-row>

    <v-card class="request-settings-card" outlined>
      <v-form
        ref="form"
        v-model="isFormValid"
        @submit.prevent="handleSubmit"
      >
        <v-row class="mt-2">
          <v-col cols="12">
            <v-text-field
              v-model="requestSettings.sender"
              label="送信元メールアドレス"
              outlined
              dense
              :rules="[
                v => !!v || 'メールアドレスは必須です',
                v => /.+@.+\..+/.test(v) || '有効なメールアドレスを入力してください'
              ]"
              @input="handleFormChange"
            ></v-text-field>
          </v-col>
        </v-row>

        <v-row>
          <v-col cols="12">
            <v-card outlined>
              <v-card-title>報告依頼を行う曜日</v-card-title>
              <v-card-subtitle>指定曜日に報告依頼メールを送信します。</v-card-subtitle>
              <v-card-text>
                <v-row no-gutters>
                  <v-col
                    v-for="day in daysOfWeek"
                    :key="day.value"
                    cols="auto"
                    class="mr-3"
                  >
                    <v-radio
                      v-model="requestSettings.requestDayOfWeek"
                      :label="day.text"
                      :value="day.value"
                      @change="handleFormChange"
                      hide-details
                    ></v-radio>
                  </v-col>
                </v-row>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <v-row class="mt-4">
          <v-col cols="12" sm="6">
            <v-select
              v-model="requestSettings.requestTime"
              :items="hours"
              item-text="text"
              item-value="value"
              label="通知時間（時）"
              outlined
              dense
              :rules="[v => !!v || '時間を選択してください']"
              @change="handleFormChange"
            ></v-select>
          </v-col>
        </v-row>

        <v-row class="mt-4">
          <v-col>
            <v-btn 
              color="primary" 
              type="submit" 
              :loading="loading"
              :disabled="!isFormValid || !isFormChanged"
            >
              <v-icon class="mr-1" left>
                mdi-check
              </v-icon>
              設定を保存する
            </v-btn>
          </v-col>
        </v-row>
      </v-form>
    </v-card>
  </v-container>
</template>

<script setup>
import { reactive, ref, onMounted, inject, toRefs, watch } from 'vue'
import { getOrganization, updateOrganization } from '../services/organizationService'
import { useStore } from 'vuex'

const store = useStore()
const organizationId = ref(store.getters['user/organizationId'])

const form = ref(null)
const showNotification = inject('showNotification')

const state = reactive({
  requestSettings: {
    sender: '',
    dayOfWeek: 'monday', // 初期値を月曜日に設定
    hour: null,
  },
  loading: false,
  isFormValid: false,
  isFormChanged: false,
  originalSettings: null
})

const { requestSettings, loading, isFormValid, isFormChanged } = toRefs(state)

const daysOfWeek = [
  { text: '月', value: 'monday' },
  { text: '火', value: 'tuesday' },
  { text: '水', value: 'wednesday' },
  { text: '木', value: 'thursday' },
  { text: '金', value: 'friday' },
  { text: '土', value: 'saturday' },
  { text: '日', value: 'sunday' },
]

const hours = Array.from({ length: 24 }, (_, i) => ({
  text: `${i.toString().padStart(2, '0')}:00`,
  value: i
}))

const handleFormChange = () => {
  isFormChanged.value = true
}

const validateForm = async () => {
  const validation = await form.value.validate()
  isFormValid.value = validation.valid && !!requestSettings.value.requestDayOfWeek
}

const handleSubmit = async () => {
  if (!isFormValid.value || !isFormChanged.value) {
    return
  }

  try {
    loading.value = true
    await updateOrganization({
      ...organizationId,
      ...requestSettings.value
    })
    showNotification('報告依頼設定を更新しました')
    console.log('Request settings updated:', requestSettings.value)
    state.originalSettings = JSON.parse(JSON.stringify(requestSettings.value))
    isFormChanged.value = false
  } catch (error) {
    showNotification('報告依頼設定の保存に失敗しました', error)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  loading.value = true
  try {
    const result = await getOrganization(organizationId)
    if (result && Object.keys(result).length > 0) {
      requestSettings.value = {
        ...result,
        hour: result.hour !== undefined ? parseInt(result.hour, 10) : null,
        dayOfWeek: result.dayOfWeek || 'monday' // データがない場合は月曜日をデフォルトに
      }
      state.originalSettings = JSON.parse(JSON.stringify(requestSettings.value))
    }
    // フォームの初期バリデーション
    await validateForm()
  } catch (error) {
    showNotification('報告依頼設定の取得に失敗しました', error)
  } finally {
    loading.value = false
  }
})

// フォームの内容が変更されたかどうかを監視
watch(
  () => JSON.stringify(requestSettings.value),
  (newVal) => {
    if (state.originalSettings) {
      isFormChanged.value = newVal !== JSON.stringify(state.originalSettings)
    }
  },
  { deep: true }
)
</script>

<style scoped>
.request-settings-container {
  max-width: 960px;
}

.request-settings-card {
  background-color: white;
  border-radius: 0.5rem;
  padding: .5em 1.5em 1em;
  position: relative;
}
</style>