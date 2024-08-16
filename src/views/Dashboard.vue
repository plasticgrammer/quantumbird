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
      <v-col cols="2" class="d-flex justify-end align-center">
        <v-icon class="me-3" @click="fetchAll">
          mdi-reload
        </v-icon>
      </v-col>
    </v-row>

    <v-row dense>
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
            - レビュー時更新メッセージ<br>
            - 確認済みは修正不可<br>
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

      <v-col
        cols="12"
        md="6"
      >
        <v-card
          class="mb-2"
        >
          <v-card-title class="text-subtitle-1">
            <v-icon
              small
              class="mr-1"
            >
              mdi-domain
            </v-icon>
            組織情報
          </v-card-title>
          <v-card-text class="pt-1 pb-3">
            <p class="text-body-1 mb-1">
              {{ organizationName }}
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
              <v-icon
                class="mr-1"
                small
                left
              >
                mdi-domain
              </v-icon>
              組織情報管理
            </v-btn>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12">
        <v-card>
          <v-card-title class="text-subtitle-1">
            <v-icon
              small
              class="mr-1"
            >
              mdi-chart-line
            </v-icon>
            個人別残業時間の遷移（過去5週間）
          </v-card-title>
          <v-card-text>
            <canvas
              ref="overtimeChart"
              height="200"
            />
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, watch, computed, onMounted } from 'vue'
import { Chart, registerables } from 'chart.js'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { useCalendar } from '../composables/useCalendar'
import { useReport } from '../composables/useReport'
import { getOrganization } from '../services/organizationService'
import { listMembers } from '../services/memberService'
import { getReportStatus, getStatsData } from '../services/reportService'
import Calendar from '../components/Calendar.vue'

Chart.register(...registerables)

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

const organizationName = ref('')
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

const overtimeChart = ref(null)
const overtimeData = ref({
  labels: [],
  datasets: []
})

const isLoading = ref(true)
const error = ref(null)

const fetchOrganizationInfo = async () => {
  try {
    const org = await getOrganization(organizationId)
    organizationName.value = org.name
  } catch (err) {
    console.error('Failed to fetch organization info:', err)
    error.value = '組織情報の取得に失敗しました'
  }
}

const fetchMembers = async () => {
  try {
    members.value = await listMembers(organizationId)
    memberCount.value = members.value.length
  } catch (err) {
    console.error('Failed to fetch members:', err)
    throw err
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
      labels: data.labels,
      datasets: data.datasets.map((dataset, index) => ({
        label: dataset.label,
        data: dataset.data.map(item => item.overtimeHours),
        borderColor: getColor(index),
        tension: 0.1,
        fill: false
      }))
    }
  } catch (err) {
    console.error('Failed to fetch overtime data:', err)
    error.value = '残業時間データの取得に失敗しました'
  }
}

// 定型カラーパレットを定義
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
    return getRandomColor()
  }
}

const getRandomColor = () => {
  const r = Math.floor(Math.random() * 255)
  const g = Math.floor(Math.random() * 255)
  const b = Math.floor(Math.random() * 255)
  return `rgb(${r}, ${g}, ${b})`
}

const initChart = () => {
  const ctx = overtimeChart.value.getContext('2d')
  new Chart(ctx, {
    type: 'line',
    data: overtimeData.value,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
        },
        title: {
          display: false
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: '残業時間'
          }
        }
      }
    }
  })
}

watch(weekIndex, () => {
  fetchReportStatus(weekString.value)
})

const fetchAll = async () => {
  await Promise.all([
    fetchOrganizationInfo(),
    fetchReportStatus(weekString.value),
    fetchStatsData(),
    fetchMembers()
  ])
}

onMounted(async () => {
  try {
    await fetchAll()
    initChart()
  } catch (err) {
    console.error('Error initializing dashboard:', err)
    error.value = 'ダッシュボードの初期化に失敗しました'
  } finally {
    isLoading.value = false
  }
})
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