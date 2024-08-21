<template>
  <v-container fluid class="p-2">
    <v-row dense class="pb-2">
      <v-col cols="10">
        <h3>
          <v-icon 
            size="large" 
            class="mr-1"
          >
            mdi-view-dashboard
          </v-icon>
          ダッシュボード
        </h3>
      </v-col>
      <v-col cols="2" class="d-flex justify-end align-center pe-3">
        <v-progress-circular 
          class="cursor-pointer" 
          size="26"
          :indeterminate="isLoading"
          @click="handleReload"
        ></v-progress-circular>
      </v-col>
    </v-row>

    <v-row v-if="!isLoading" dense>
      <v-col cols="12">
        <v-card
          class="mb-2"
        >
          <v-card-title class="text-subtitle-1">
            <v-icon
              small
              class="mr-1"
            >
              mdi-calendar-multiple-check
            </v-icon>
            報告状況
          </v-card-title>
          <v-card-text class="pt-1 pb-3">
            <v-row class="pb-1">
              <v-col cols="12" md="9">
                <v-card max-width="560" class="mx-auto calendar-card">
                  <v-container class="pa-0 position-relative">
                    <div v-for="(week, index) in calendarWeeks" :key="index" :class="{ 'd-none': index !== weekIndex }">
                      <Calendar :calendar-weeks="[week]" />
                    </div>
                    <v-btn
                      v-if="weekIndex > 0"
                      class="calendar-nav-btn calendar-nav-btn-left"
                      icon="mdi-arrow-left-thick"
                      size="small"
                      fab
                      @click="weekIndex = Math.max(0, weekIndex - 1)"
                    ></v-btn>
                    <v-btn
                      v-if="weekIndex < calendarWeeks.length - 1"
                      class="calendar-nav-btn calendar-nav-btn-right"
                      icon="mdi-arrow-right-thick"
                      size="small"
                      fab
                      @click="weekIndex = Math.min(calendarWeeks.length - 1, weekIndex + 1)"
                    ></v-btn>
                  </v-container>
                </v-card>
                <v-badge 
                  class="mt-6"
                  :color="statusCounts['pending'] ? 'info' : 'transparent'"
                  :content="statusCounts['pending'] || ''"
                >
                  <v-btn 
                    v-if="isAdmin" color="black" variant="outlined"
                    :to="{ name: 'WeeklyReview', params: { weekString } }" x-small
                  >
                    <v-icon class="mr-1" small left>
                      mdi-calendar-multiple-check
                    </v-icon>
                    週次報告レビュー
                  </v-btn>
                </v-badge>
              </v-col>
              <v-col cols="12" md="3" class="d-flex flex-sm-column align-start pt-2">
                <span v-for="status in filteredStatusOptions" :key="status.value">
                  <v-chip
                    v-if="statusCounts[status.value] > 0"
                    class="ma-1"
                    :value="status.value"
                    :color="status.color"
                    label
                  >
                    {{ status.text }}: {{ statusCounts[status.value] }}
                  </v-chip>                  
                </span>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="6">
        <v-card
          class="mb-2"
        >
          <v-card-title class="text-subtitle-1">
            <v-icon
              small
              class="mr-1"
            >
              mdi-clipboard-check-outline
            </v-icon>
            やることリスト
          </v-card-title>
          <v-card-text class="pt-1 pb-3">
            - レビュー時 報告並び順<br>
            - サインアウト<br>
            - 確認済みは修正不可△<br>
            - 報告済みステータスをカレンダーに表示<br>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="6">
        <v-card
          class="mb-2"
        >
          <v-card-title class="text-subtitle-1">
            <v-icon
              small
              class="mr-1"
            >
              mdi-calendar-multiple-check
            </v-icon>
            【テスト用】メンバーの週次報告
          </v-card-title>
          <v-card-text class="pt-1 pb-3">
            <v-row>
              <v-col>
                <v-select
                  v-model="selectedMember"
                  :items="members"
                  item-title="name"
                  item-value="memberUuid"
                  label="メンバー選択"
                  class="mb-2"
                  density="comfortable"
                  variant="outlined"
                  hide-details
                ></v-select>
              </v-col>
              <v-col>
                <v-btn
                  color="black"
                  variant="outlined"
                  :href="weeklyReportLink"
                  target="_blank"
                  rel="noopener noreferrer"
                  :disabled="!selectedMember"
                  x-small
                >
                  週次報告
                  <v-icon icon="mdi-open-in-new" end small />
                </v-btn>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="6">
        <v-card class="mb-2">
          <v-card-title class="text-subtitle-1">
            <v-icon small class="mr-1">
              mdi-domain
            </v-icon>
            組織情報
          </v-card-title>
          <v-card-text class="pt-1 pb-3">
            <p class="text-body-1 mb-1">
              {{ organization.name }}
            </p>
            <p class="text-body-2 mb-1">
              メンバー: {{ memberCount }} 人
            </p>
            <v-btn
              v-if="isAdmin"
              color="black"
              variant="outlined"
              :to="{ name: 'OrganizationManagement' }"
              class="mt-3"
              x-small
            >
              <v-icon class="mr-1" small>
                mdi-domain
              </v-icon>
              組織情報管理
            </v-btn>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="6">
        <v-card class="mb-2">
          <v-card-title class="text-subtitle-1">
            <v-icon small class="mr-1">
              mdi-mail
            </v-icon>
            報告依頼
          </v-card-title>
          <v-card-text class="pt-1 pb-3">
            <p class="text-body-2 mb-1">
              <span>自動報告設定: </span>
              <v-icon
                :color="organization.requestEnabled ? 'success' : 'error'"
                size="small"
                class="mx-1"
              >
                {{ organization.requestEnabled ? 'mdi-check-circle' : 'mdi-close-circle' }}
              </v-icon>
              <span class="text-subtitle-1">
                <strong>{{ organization.requestEnabled ? '有効' : '無効' }}</strong>
              </span>
            </p>
            <p v-if="organization.requestEnabled && nextRequestDateTime" class="text-body-2 mb-1">
              <span class="mr-2">次回報告依頼日時: </span>
              <span class="text-subtitle-1">{{ formatDate(nextRequestDateTime) }}</span>
            </p>
            <v-btn
              v-if="isAdmin"
              color="black"
              variant="outlined"
              :to="{ name: 'RequestSetting' }"
              class="mt-3"
              x-small
            >
              <v-icon class="mr-1" small>
                mdi-mail
              </v-icon>
              報告依頼設定
            </v-btn>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="6">
        <v-card>
          <v-card-title class="text-subtitle-1">
            <v-icon small class="mr-1">
              mdi-chart-line
            </v-icon>
            残業時間の遷移（過去5週間）
          </v-card-title>
          <v-card-text class="pb-1">
            <OvertimeChart :chart-data="overtimeData" />
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="6">
        <v-card>
          <v-card-title class="text-subtitle-1">
            <v-icon small class="mr-1">
              mdi-chart-line
            </v-icon>
            ストレス評価の遷移（過去5週間）
          </v-card-title>
          <v-card-text class="pb-1">
            <StressChart :chart-data="stressData" />
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, watch, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { useCalendar } from '../composables/useCalendar'
import { useReport } from '../composables/useReport'
import { getOrganization } from '../services/organizationService'
import { getReportStatus, getStatsData } from '../services/reportService'
import Calendar from '../components/Calendar.vue'
import OvertimeChart from '../components/chart/OvertimeChart.vue'
import StressChart from '../components/chart/StressChart.vue'

const store = useStore()
const router = useRouter()
const { createWeeks, getStringFromWeek } = useCalendar()
const { statusOptions } = useReport()

const organizationId = store.getters['user/organizationId']
const isAdmin = ref(true)
const calendarWeeks = createWeeks(6)
const weekIndex = ref(calendarWeeks.length - 1)
const weekString = computed(() => getStringFromWeek(calendarWeeks[weekIndex.value]))

const filteredStatusOptions = statusOptions.filter(option => option.value !== 'all')
const statusCounts = computed(() => {
  const counts = {
    none: memberCount.value - reportStatus.value.reportedCount,
    pending: reportStatus.value.pending,
    feedback: reportStatus.value.inFeedback,
    approved: reportStatus.value.confirmed
  }
  return counts
})

const organization = ref('')
const reportStatus = ref({
  pending: 0,
  inFeedback: 0,
  confirmed: 0
})
const memberCount = ref(null)
const members = ref([])
const selectedMember = ref(null)
const weeklyReportLink = computed(() => {
  if (!selectedMember.value) return '#'
  const route = router.resolve({
    name: 'WeeklyReport',
    params: {
      organizationId,
      memberUuid: selectedMember.value,
      weekString: weekString.value
    }
  })
  return route.href
})

const isLoading = ref(true)
const error = ref(null)

const dayOfWeekToNumber = {
  sunday: 0,
  monday: 1,
  tuesday: 2,
  wednesday: 3,
  thursday: 4,
  friday: 5,
  saturday: 6
}

const nextRequestDateTime = computed(() => {
  if (!organization.value?.requestEnabled) {
    return null
  }

  const { requestDayOfWeek, requestTime } = organization.value
  const dayOfWeek = dayOfWeekToNumber[requestDayOfWeek.toLowerCase()]
  const [hours, minutes] = requestTime.split(':').map(Number)

  if (dayOfWeek === undefined || isNaN(hours) || isNaN(minutes)) {
    console.error('Invalid input data:', { dayOfWeek, hours, minutes })
    return null
  }

  const now = new Date()
  let nextDate = new Date(now.getFullYear(), now.getMonth(), now.getDate(), hours, minutes, 0, 0)

  // 今日が報告日で、現在時刻が報告時間より前の場合はそのまま返す
  if (nextDate.getDay() === dayOfWeek && nextDate > now) {
    return nextDate
  }

  // 次の報告日まで日数を加算
  const daysUntilNext = (dayOfWeek - now.getDay() + 7) % 7
  nextDate.setDate(nextDate.getDate() + (daysUntilNext === 0 ? 7 : daysUntilNext))
  
  return nextDate
})

const formatDate = (date) => {
  const weekdays = ['日', '月', '火', '水', '木', '金', '土']
  const year = date.getFullYear()
  const month = date.getMonth() + 1 // getMonth() は 0-11 を返すため、+1 する
  const day = date.getDate()
  const weekday = weekdays[date.getDay()]
  const hour = date.getHours().toString().padStart(2, '0')
  const minute = date.getMinutes().toString().padStart(2, '0')

  return `${year}-${month}-${day} (${weekday})  ${hour}:${minute}`
}

const fetchOrganizationInfo = async () => {
  try {
    const org = await getOrganization(organizationId)
    organization.value = org
    members.value = org.members
    memberCount.value = members.value.length
  } catch (err) {
    console.error('Failed to fetch organization info:', err)
    error.value = '組織情報の取得に失敗しました'
  }
}

const fetchReportStatus = async (weekString) => {
  try {
    const status = await getReportStatus(organizationId, weekString)
    reportStatus.value = {
      ...status,
      reportedCount: status.pending + status.inFeedback + status.confirmed,
      totalCount: status.totalCount || 0
    }
  } catch (err) {
    console.error('Failed to fetch report status:', err)
    error.value = '報告状況の取得に失敗しました'
  }
}

const fetchStatsData = async () => {
  try {
    const data = await getStatsData(organizationId)
    overtimeData.value = {
      labels: data.labels.map(label => label.split('-')[1]),
      datasets: data.datasets.map((dataset, index) => ({
        label: dataset.label,
        data: dataset.data.map(item => item.overtimeHours),
        borderColor: getColor(index),
        tension: 0.1,
        fill: false
      }))
    }
    stressData.value = {
      labels: data.labels.map(label => label.split('-')[1]),
      datasets: data.datasets.map((dataset, index) => ({
        label: dataset.label,
        data: dataset.data.map(item => item.stress || 0),
        borderColor: getColor(index),
        tension: 0.1,
        fill: false
      }))
    }
  } catch (err) {
    console.error('Failed to fetch stats data:', err)
    error.value = '統計データの取得に失敗しました'
  }
}

const colorPalette = [
  'rgb(54, 162, 235)', // 青
  'rgb(75, 192, 192)', // 緑
  'rgb(199, 199, 199)', // グレー
  'rgb(255, 99, 132)', // 赤
  'rgb(255, 206, 86)', // 黄
  'rgb(153, 102, 255)', // 紫
  'rgb(255, 159, 64)', // オレンジ
  'rgb(83, 102, 255)' // 青紫
]

// 色を取得する関数
const getColor = (index) => {
  if (index < colorPalette.length) {
    return colorPalette[index]
  } else {
    const r = Math.floor(Math.random() * 255)
    const g = Math.floor(Math.random() * 255)
    const b = Math.floor(Math.random() * 255)
    return `rgb(${r}, ${g}, ${b})`
  }
}

const overtimeData = ref({
  labels: [],
  datasets: []
})

const stressData = ref({
  labels: [],
  datasets: []
})

watch(weekIndex, () => {
  fetchReportStatus(weekString.value)
})

const fetchAll = async () => {
  isLoading.value = true
  try {
    await Promise.all([
      fetchOrganizationInfo(),
      fetchReportStatus(weekString.value),
      fetchStatsData()
    ])
    // initChart の呼び出しを削除
  } catch (err) {
    console.error('Error initializing dashboard:', err)
    error.value = 'ダッシュボードの初期化に失敗しました'
  } finally {
    isLoading.value = false
  }
}

// リロードボタンのクリックハンドラ
const handleReload = () => {
  fetchAll()
}

onMounted(fetchAll)
</script>

<style scoped>
.calendar-small :deep(.v-date-picker-month) {
  height: 240px;
}

.calendar-small :deep(.v-date-picker-month__day) {
  width: 28px;
  height: 28px;
  font-size: 0.9rem;
}

.calendar-small :deep(.v-date-picker-controls) {
  display: none;
}

.calendar-card {
  overflow: visible !important;
}

.position-relative {
  position: relative;
}

.calendar-nav-btn {
  opacity: 0.6;
  position: absolute;
  bottom: 6px;
}

.calendar-nav-btn-left {
  left: -30px;
}

.calendar-nav-btn-right {
  right: -30px;
}
</style>