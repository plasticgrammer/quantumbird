<template>
  <v-container fluid class="p-2">
    <v-row dense class="pb-2">
      <v-col cols="10">
        <h3>
          <v-icon 
            size="large" 
            class="mr-1"
            aria-hidden="true"
          >
            mdi-view-dashboard
          </v-icon>
          ダッシュボード
        </h3>
      </v-col>
      <v-col cols="2" class="d-flex justify-end align-center pe-3">
        <v-icon
          icon="mdi-reload"
          aria-label="データを更新"
          @click="handleReload"
        ></v-icon>
      </v-col>
    </v-row>

    <v-row v-if="!isLoading" dense>
      <v-col cols="12" class="mb-2">
        <v-card class="widget">
          <v-card-title class="text-subtitle-1">
            <v-icon
              small
              class="mr-1"
              aria-hidden="true"
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
                      aria-label="前の週へ"
                      @click="weekIndex = Math.max(0, weekIndex - 1)"
                    ></v-btn>
                    <v-btn
                      v-if="weekIndex < calendarWeeks.length - 1"
                      class="calendar-nav-btn calendar-nav-btn-right"
                      icon="mdi-arrow-right-thick"
                      size="small"
                      fab
                      aria-label="次の週へ"
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
                    color="black" variant="outlined"
                    :to="{ name: 'WeeklyReview', params: { weekString } }"
                    aria-label="週次報告レビューへ移動"
                  >
                    <v-icon class="mr-1" small left aria-hidden="true">
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

      <v-col cols="12" md="6" class="mb-2">
        <v-card class="widget">
          <v-card-title class="text-subtitle-1">
            <v-icon small class="mr-1" aria-hidden="true">
              mdi-chart-line
            </v-icon>
            残業時間の遷移（過去5週間）
          </v-card-title>
          <v-card-text class="pb-1">
            <Suspense v-if="isOvertimeDataReady">
              <template #default>
                <OvertimeChart :chart-data="overtimeData" />
              </template>
              <template #fallback>
                <div aria-live="polite">残業時間チャートを読み込み中...</div>
              </template>
            </Suspense>
            <div v-else aria-live="polite">残業時間データを準備中...</div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="6" class="mb-2">
        <v-card class="widget">
          <v-card-title class="text-subtitle-1">
            <v-icon small class="mr-1" aria-hidden="true">
              mdi-chart-line
            </v-icon>
            ストレス評価の遷移（過去5週間）
          </v-card-title>
          <v-card-text class="pb-1">
            <Suspense v-if="isStressDataReady">
              <template #default>
                <StressChart :chart-data="stressData" />
              </template>
              <template #fallback>
                <div aria-live="polite">ストレス評価チャートを読み込み中...</div>
              </template>
            </Suspense>
            <div v-else aria-live="polite">ストレス評価データを準備中...</div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="6" class="mb-2">
        <v-card class="widget">
          <v-card-title class="text-subtitle-1">
            <v-icon small class="mr-1" aria-hidden="true">
              mdi-domain
            </v-icon>
            組織情報
          </v-card-title>
          <v-card-text class="pt-2 pb-3">
            <p class="text-body-1 mb-2">
              {{ organization.name }}
            </p>
            <p class="text-body-2 mb-1">
              メンバー: {{ memberCount }} 人
            </p>
            <v-btn
              color="black" variant="outlined" class="mt-3"
              :to="{ name: 'OrganizationManagement' }"
              aria-label="組織情報管理ページへ移動"
            >
              <v-icon class="mr-1" small aria-hidden="true">
                mdi-domain
              </v-icon>
              組織情報管理
            </v-btn>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="6" class="mb-2">
        <v-card class="widget">
          <v-card-title class="text-subtitle-1">
            <v-icon small class="mr-1" aria-hidden="true">
              mdi-mail
            </v-icon>
            報告依頼
          </v-card-title>
          <v-card-text class="pt-1 pb-3">
            <p class="text-body-2 mb-1">
              <span>自動報告依頼設定: </span>
              <v-icon
                :color="organization.requestEnabled ? 'success' : 'grey'"
                class="mx-1"
                aria-hidden="true"
              >
                {{ organization.requestEnabled ? 'mdi-timer-outline' : 'mdi-timer-off-outline' }}
              </v-icon>
              <span class="text-subtitle-1">
                <strong>{{ organization.requestEnabled ? '有効' : '無効' }}</strong>
              </span>
            </p>
            <p v-if="organization.requestEnabled && nextRequestDateTime" class="text-body-2 mb-1">
              <span class="mr-2">次回報告依頼日時: </span>
              <span class="text-subtitle-1">{{ formatFullDateTimeJp(nextRequestDateTime) }}</span>
            </p>
            <v-btn
              color="black" variant="outlined" class="mt-3"
              :to="{ name: 'RequestSetting' }"
              aria-label="報告依頼設定ページへ移動"
            >
              <v-icon class="mr-1" small aria-hidden="true">
                mdi-mail
              </v-icon>
              報告依頼設定
            </v-btn>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="6" class="mb-2">
        <TodoListCard />
      </v-col>

      <v-col cols="12" md="6" class="mb-2">
        <v-card class="widget">
          <v-card-title class="text-subtitle-1">
            <v-icon small class="mr-1" aria-hidden="true">
              mdi-calendar-account
            </v-icon>
            メンバーの週次報告
          </v-card-title>
          <v-card-text class="pt-1 pb-3">
            <v-row>
              <v-col cols="6">
                <v-select
                  v-model="selectedMember"
                  :items="members"
                  item-title="name"
                  item-value="memberUuid"
                  label="メンバー選択"
                  density="comfortable"
                  variant="outlined"
                  hide-details
                ></v-select>
              </v-col>
              <v-col cols="12">
                <v-btn
                  color="black"
                  variant="outlined"
                  :href="weeklyReportLink"
                  target="_blank"
                  rel="noopener noreferrer"
                  :disabled="!selectedMember"
                  x-small
                  aria-label="選択したメンバーの週次報告ページを新しいタブで開く"
                >
                  週次報告（代理入力）
                  <v-icon icon="mdi-open-in-new" end small aria-hidden="true" />
                </v-btn>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, computed, watch, onMounted, defineAsyncComponent, nextTick } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { useCalendar } from '../composables/useCalendar'
import { useReport } from '../composables/useReport'
import { getOrganization } from '../services/organizationService'
import { getReportStatus, getStatsData } from '../services/reportService'
import Calendar from '../components/Calendar.vue'
const OvertimeChart = defineAsyncComponent(() => import('../components/chart/OvertimeChart.vue'))
const StressChart = defineAsyncComponent(() => import('../components/chart/StressChart.vue'))
const TodoListCard = defineAsyncComponent(() => import('../components/widget/TodoListCard.vue'))

const store = useStore()
const router = useRouter()
const { createWeeks, getStringFromWeek, formatFullDateTimeJp } = useCalendar()
const { statusOptions } = useReport()

const dayOfWeekToNumber = {
  sunday: 0,
  monday: 1,
  tuesday: 2,
  wednesday: 3,
  thursday: 4,
  friday: 5,
  saturday: 6
}

const organizationId = store.getters['auth/organizationId']
const calendarWeeks = createWeeks(6)
const weekIndex = ref(null)

const organization = ref(null)
const reportStatus = ref({
  pending: 0,
  inFeedback: 0,
  confirmed: 0,
  reportedCount: 0,
  totalCount: 0,
})
const selectedMember = ref(null)
const isLoading = ref(true)
const error = ref(null)
const isOvertimeDataReady = ref(false)
const isStressDataReady = ref(false)

const overtimeData = ref({ labels: [], datasets: [] })
const stressData = ref({ labels: [], datasets: [] })

// Computed properties
const members = computed(() => organization.value?.members || [])
const memberCount = computed(() => members.value.length)
const weekString = computed(() => getStringFromWeek(calendarWeeks[weekIndex.value]))
const filteredStatusOptions = computed(() => 
  statusOptions.filter(option => option.value !== 'all')
)

const statusCounts = computed(() => ({
  none: memberCount.value - reportStatus.value.reportedCount,
  pending: reportStatus.value.pending,
  feedback: reportStatus.value.inFeedback,
  approved: reportStatus.value.confirmed,
}))

const weeklyReportLink = computed(() => {
  if (!selectedMember.value) return '#'
  return router.resolve({
    name: 'WeeklyReport',
    params: {
      organizationId: organizationId,
      memberUuid: selectedMember.value,
      weekString: weekString.value,
    },
  }).href
})

const nextRequestDateTime = computed(() => {
  if (!organization.value?.requestEnabled) {
    return null
  }

  const { requestDayOfWeek, requestTime } = organization.value
  const dayOfWeek = dayOfWeekToNumber[requestDayOfWeek.toLowerCase()]
  const [hours, minutes] = requestTime.split(':').map(Number)

  if (dayOfWeek === undefined || isNaN(hours) || isNaN(minutes)) {
    console.error('Invalid organization data:', { requestDayOfWeek, requestTime })
    return null
  }

  const now = new Date()
  let nextDate = new Date(now.getFullYear(), now.getMonth(), now.getDate(), hours, minutes, 0, 0)

  if (nextDate.getDay() === dayOfWeek && nextDate > now) {
    return nextDate
  }

  const daysUntilNext = (dayOfWeek - now.getDay() + 7) % 7
  nextDate.setDate(nextDate.getDate() + (daysUntilNext === 0 ? 7 : daysUntilNext))
  
  return nextDate
})

const fetchReportStatus = async () => {
  try {
    const status = await getReportStatus(organizationId, weekString.value)
    reportStatus.value = {
      ...status,
      reportedCount: status.pending + status.inFeedback + status.confirmed,
      totalCount: status.totalCount || 0,
    }
  } catch (err) {
    console.error('Failed to fetch report status:', err)
    error.value = '報告状況の取得に失敗しました: ' + err.message
    throw err
  }
}

const formatChartData = (data, dataKey) => ({
  labels: data.labels,
  datasets: data.datasets.map((dataset, index) => ({
    label: dataset.label,
    data: dataset.data.map(item => item[dataKey]),
    borderColor: getColor(index),
    tension: 0.1,
    fill: false,
  })),
})

const getColor = (index) => {
  const colorPalette = [
    'rgb(54, 162, 235)', 'rgb(75, 192, 192)', 'rgb(199, 199, 199)', 
    'rgb(255, 99, 132)', 'rgb(153, 102, 255)', 'rgb(255, 159, 64)', 
    'rgb(83, 102, 255)', 'rgb(255, 206, 86)'
  ]
  return index < colorPalette.length ? colorPalette[index] : getRandomColor()
}

const getRandomColor = () => {
  const r = Math.floor(Math.random() * 255)
  const g = Math.floor(Math.random() * 255)
  const b = Math.floor(Math.random() * 255)
  return `rgb(${r}, ${g}, ${b})`
}

const fetchInitial = async () => {
  isLoading.value = true
  error.value = null
  try {
    const [orgInfo, reportStatus] = await Promise.all([
      getOrganization(organizationId),
      getReportStatus(organizationId, weekString.value)
    ])
    
    organization.value = orgInfo
    reportStatus.value = {
      ...reportStatus,
      reportedCount: reportStatus.pending + reportStatus.inFeedback + reportStatus.confirmed,
      totalCount: reportStatus.totalCount || 0,
    }
  } catch (err) {
    console.error('Error initializing dashboard:', err)
    error.value = 'ダッシュボードの初期化に失敗しました: ' + err.message
  } finally {
    isLoading.value = false
  }
}

const fetchSecondary = async () => {
  try {
    const statsData = await getStatsData(organizationId)
    overtimeData.value = formatChartData(statsData, 'overtimeHours')
    stressData.value = formatChartData(statsData, 'stress')
    isOvertimeDataReady.value = true
    isStressDataReady.value = true
  } catch (err) {
    console.error('Error fetching secondary data:', err)
    error.value = '追加データの取得に失敗しました: ' + err.message
  }
}

const handleReload = () => {
  fetchInitial()
  nextTick(() => {
    fetchSecondary()
  })
}

// Watchers
watch(weekIndex, fetchReportStatus)

// Lifecycle hooks
onMounted(() => {
  weekIndex.value = calendarWeeks.length - 2// 先週
  fetchInitial()
  nextTick(() => {
    fetchSecondary()
  })
})
</script>

<style scoped>
.widget {
  min-height: 165px;
}

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