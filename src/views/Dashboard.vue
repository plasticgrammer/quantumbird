<template>
  <v-container fluid class="p-2">
    <v-row 
      dense 
      class="pb-4"
    >
      <v-col>
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
                      class="calendar-nav-btn calendar-nav-btn-left"
                      icon="mdi-arrow-left-thick"
                      size="small"
                      fab
                      @click="weekIndex = Math.max(0, weekIndex - 1)"
                    ></v-btn>
                    <v-btn
                      class="calendar-nav-btn calendar-nav-btn-right"
                      icon="mdi-arrow-right-thick"
                      size="small"
                      fab
                      @click="weekIndex = Math.min(calendarWeeks.length - 1, weekIndex + 1)"
                    ></v-btn>
                  </v-container>
                </v-card>
              </v-col>
              <v-col cols="12" md="3" class="d-flex flex-column align-start">
                <v-chip v-if="((memberCount - reportStatus.reportedCount) || 0) > 0" class="status-chip ma-1" color="error" label>
                  報告なし: {{ (memberCount - reportStatus.reportedCount) || 0 }}
                </v-chip>
                <v-chip v-if="reportStatus.pending > 0" class="status-chip ma-1" color="primary" label>
                  確認待ち: {{ reportStatus.pending }}
                </v-chip>
                <v-chip v-if="reportStatus.inFeedback > 0" class="status-chip ma-1" color="warning" label>
                  フィードバック中: {{ reportStatus.inFeedback }}
                </v-chip>
                <v-chip class="status-chip ma-1" color="success" label>
                  確認済み: {{ reportStatus.confirmed }}
                </v-chip>
              </v-col>
            </v-row>
            <v-btn
              v-if="isAdmin"
              color="primary"
              class="mt-3"
              :to="{ name: 'WeeklyReview', params: { weekString } }"
              x-small
            >
              <v-icon class="mr-1" small left>
                mdi-calendar-multiple-check
              </v-icon>
              週次報告レビュー
            </v-btn>
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
            - 押下可能なチップと表示チップの見分け<br>
            - 現状を☆で評価<br>
            - 報告画面に名前表示<br>
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
            メンバーの週次報告
          </v-card-title>
          <v-card-text class="pt-1 pb-3">
            <v-btn
              color="secondary"
              :to="{ name: 'WeeklyReportSelector', params: { organizationId: 'jsp-d3', memberUuid: 'd35cdaa4-07f5-4283-8222-cb338d0a06ee' } }"
              x-small
            >
              週報 0001
            </v-btn>
            <span class="px-3" />
            <v-btn
              color="secondary"
              :to="{ name: 'WeeklyReportSelector', params: { organizationId: 'jsp-d3', memberUuid: 'd4435e05-1dbc-4533-82cb-64b96d94bcad' } }"
              x-small
            >
              週報 0009
            </v-btn>
            <span class="px-3" />
            <v-btn
              color="secondary"
              :to="{ name: 'WeeklyReportSelector', params: { organizationId: 'jsp-d3', memberUuid: 'c5b7ec52-2c39-4a8e-bc92-e854108f6825' } }"
              x-small
            >
              週報 0027
            </v-btn>
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
              color="primary"
              :to="{ name: 'OrganizationManagement' }"
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
import { getOrganization } from '../services/organizationService'
import { listMembers } from '../services/memberService'
import { getReportStatus, getOvertimeData } from '../services/reportService'
import { useCalendar } from '../composables/useCalendar'
import Calendar from '../components/Calendar.vue'

const {
  createWeeks,
  getStringFromWeek
} = useCalendar()

Chart.register(...registerables)

const store = useStore()
const organizationId = store.getters['user/organizationId']
const isAdmin = ref(true)
const calendarWeeks = createWeeks(6)
const weekIndex = ref(calendarWeeks.length - 1)
const weekString = computed(() => getStringFromWeek(calendarWeeks[weekIndex.value]))

const organizationName = ref('')
const reportStatus = ref({
  pending: 0,
  inFeedback: 0,
  confirmed: 0
})
const memberCount = ref(null)

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
    const members = await listMembers(organizationId)
    memberCount.value = members.length
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

const fetchOvertimeData = async () => {
  try {
    const data = await getOvertimeData(organizationId)
    overtimeData.value = {
      labels: data.labels,
      datasets: data.datasets.map((dataset, index) => ({
        ...dataset,
        borderColor: getColor(index),
        tension: 0.1
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

onMounted(async () => {
  try {
    await Promise.all([
      fetchOrganizationInfo(),
      fetchReportStatus(weekString.value),
      fetchOvertimeData(),
      fetchMembers()
    ])
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