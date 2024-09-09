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
        <v-icon
          icon="mdi-reload"
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

      <v-col cols="12" md="6" class="mb-2">
        <v-card class="widget">
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

      <v-col cols="12" md="6" class="mb-2">
        <v-card class="widget">
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

      <v-col cols="12" md="6" class="mb-2">
        <v-card class="widget">
          <v-card-title class="text-subtitle-1">
            <v-icon small class="mr-1">
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

      <v-col cols="12" md="6" class="mb-2">
        <v-card class="widget">
          <v-card-title class="text-subtitle-1">
            <v-icon small class="mr-1">
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
              >
                {{ organization.requestEnabled ? 'mdi-timer-outline' : 'mdi-timer-off-outline' }}
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

      <v-col cols="12" md="6" class="mb-2">
        <v-card class="widget">
          <v-card-title class="text-subtitle-1 d-flex justify-space-between align-center">
            <div class="mb-1">
              <v-icon small class="mr-1">
                mdi-clipboard-check-outline
              </v-icon>
              やることリスト
            </div>
            <v-btn
              v-if="hasCompletedTasks"
              color="error"
              size="small"
              variant="outlined"
              @click="clearCompletedTasks"
            >
              完了済み削除
            </v-btn>
          </v-card-title>
          <v-card-text class="pb-4">
            <div v-if="tasks.length > 0" class="pa-0">
              <v-checkbox
                v-for="task in tasks"
                :key="task.taskId"
                v-model="task.completed"
                color="info"
                class="todo-item pa-0"
                :label="task.title"
                hide-details
                density="compact"
                @change="handleTaskCompletion(task)"
              >
                <template #label>
                  <span :class="{ 'text-decoration-line-through': task.completed }">
                    {{ task.title }}
                  </span>
                </template>
              </v-checkbox>
            </div>
            <p v-else>タスクがありません</p>
            <v-text-field
              v-model="newTaskTitle"
              label="新しいタスク"
              hide-details
              single-line
              density="compact"
              class="mt-2"
              append-inner-icon="mdi-plus"
              @click:append-inner="addTask"
              @keydown.enter="handleNewTaskKeydown($event)"
            ></v-text-field>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="6" class="mb-2">
        <v-card class="widget">
          <v-card-title class="text-subtitle-1">
            <v-icon small class="mr-1">
              mdi-calendar-account
            </v-icon>
            メンバーの週次報告（代理入力）
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
                >
                  週次報告
                  <v-icon icon="mdi-open-in-new" end small />
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
import { ref, computed, watch, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { useCalendar } from '../composables/useCalendar'
import { useReport } from '../composables/useReport'
import { getOrganization } from '../services/organizationService'
import { getReportStatus, getStatsData } from '../services/reportService'
import { submitUserTasks, updateUserTasks, deleteUserTasks, listUserTasks } from '../services/userTasksService'
import Calendar from '../components/Calendar.vue'
import OvertimeChart from '../components/chart/OvertimeChart.vue'
import StressChart from '../components/chart/StressChart.vue'

const store = useStore()
const router = useRouter()
const { createWeeks, getStringFromWeek } = useCalendar()
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
const isAdmin = ref(true)
const calendarWeeks = createWeeks(6)
const weekIndex = ref(calendarWeeks.length - 2) // 先週

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

const formatDate = (date) => {
  if (!(date instanceof Date)) {
    console.error('Invalid date object:', date)
    return ''
  }
  
  const weekdays = ['日', '月', '火', '水', '木', '金', '土']
  const year = date.getFullYear()
  const month = date.getMonth() + 1 // getMonth() returns 0-11
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
  } catch (err) {
    console.error('Failed to fetch organization info:', err)
    error.value = '組織情報の取得に失敗しました: ' + err.message
    throw err
  }
}

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

const fetchStatsData = async () => {
  try {
    const data = await getStatsData(organizationId)
    overtimeData.value = formatChartData(data, 'overtimeHours')
    stressData.value = formatChartData(data, 'stress')
  } catch (err) {
    console.error('Failed to fetch stats data:', err)
    error.value = '統計データの取得に失敗しました: ' + err.message
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
    'rgb(255, 99, 132)', 'rgb(255, 206, 86)', 'rgb(153, 102, 255)', 
    'rgb(255, 159, 64)', 'rgb(83, 102, 255)'
  ]
  return index < colorPalette.length ? colorPalette[index] : getRandomColor()
}

const getRandomColor = () => {
  const r = Math.floor(Math.random() * 255)
  const g = Math.floor(Math.random() * 255)
  const b = Math.floor(Math.random() * 255)
  return `rgb(${r}, ${g}, ${b})`
}

const tasks = ref([])
const newTaskTitle = ref('')
const hasCompletedTasks = computed(() => tasks.value.some(task => task.completed))

const fetchTasks = async () => {
  try {
    const userId = store.getters['auth/cognitoUserSub']
    if (!userId) {
      console.error('User ID is not available')
      return
    }

    const response = await listUserTasks(userId)
    if (response && Array.isArray(response)) {
      tasks.value = response
    } else {
      tasks.value = []
    }
  } catch (err) {
    console.error('タスクの取得に失敗しました:', err)
    tasks.value = []
  }
}

const handleNewTaskKeydown = async (event) => {
  if (event.key === 'Enter' && !event.isComposing) {
    event.preventDefault()
    await addTask()
  }
}

const addTask = async () => {
  const userId = store.getters['auth/cognitoUserSub']
  if (newTaskTitle.value.trim() && userId) {
    try {
      const newTask = {
        title: newTaskTitle.value.trim(),
        userId: userId,
        createdAt: new Date().toISOString(),
        completed: false
      }
      const response = await submitUserTasks(newTask)
      tasks.value.push(response)
      newTaskTitle.value = ''
    } catch (error) {
      console.error('タスクの追加に失敗しました:', error)
    }
  }
}

const handleTaskCompletion = async (task) => {
  try {
    await updateUserTasks({
      ...task,
      completed: task.completed
    })
  } catch (error) {
    console.error('タスクの更新に失敗しました:', error)
    task.completed = !task.completed // エラーの場合、UI上で元の状態に戻す
  }
}

const clearCompletedTasks = async () => {
  const userId = store.getters['auth/cognitoUserSub']
  if (!userId) {
    console.error('User ID is not available')
    return
  }

  const completedTasks = tasks.value.filter(task => task.completed)
  
  error.value = null
  try {
    await Promise.all(completedTasks.map(task => deleteUserTasks(userId, task.taskId)))
    tasks.value = tasks.value.filter(task => !task.completed)
  } catch (err) {
    console.error('完了済みタスクの削除に失敗しました:', err)
    error.value = '完了済みタスクの削除中にエラーが発生しました。'
  }
}

const fetchAll = async () => {
  isLoading.value = true
  error.value = null
  try {
    await Promise.all([
      fetchOrganizationInfo(),
      fetchReportStatus(),
      fetchStatsData(),
      fetchTasks()
    ])
  } catch (err) {
    console.error('Error initializing dashboard:', err)
    error.value = 'ダッシュボードの初期化に失敗しました: ' + err.message
  } finally {
    isLoading.value = false
  }
}

const handleReload = () => {
  fetchAll()
}

// Watchers
watch(weekIndex, fetchReportStatus)

// Lifecycle hooks
onMounted(fetchAll)
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

.todo-item :deep() .v-selection-control {
  min-height: 1.2em !important;
}

.todo-item :deep() .v-label {
  padding-left: 8px;
}
</style>