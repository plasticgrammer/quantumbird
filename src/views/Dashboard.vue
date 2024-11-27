<template>
  <v-container>
    <v-row dense class="pb-4">
      <v-col cols="8">
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
      <v-col cols="4" class="d-flex justify-end align-center pe-3">
        <v-btn
          v-tooltip="isReordering ? 'ウィジェットの並び替えを完了' : 'ウィジェットの並び替えモードに切り替え'"
          :icon="isReordering ? 'mdi-check' : 'mdi-drag'"
          :aria-label="isReordering ? '並び替えを完了' : 'ウィジェットを並び替え'"
          class="opacity-80 me-2"
          density="comfortable"
          @click="isReordering = !isReordering"
        ></v-btn>
        <v-btn
          v-tooltip="'データを最新の状態に更新'"
          icon="mdi-reload"
          aria-label="データを更新"
          class="opacity-80"
          density="comfortable"
          @click="handleReload"
        ></v-btn>
      </v-col>
    </v-row>

    <v-row v-if="!isLoading" dense>
      <v-container fluid class="widgets-container pa-0">
        <VueDraggable
          :model-value="sortableWidgets"
          :component-data="{
            tag: 'div',
            type: 'transition-group',
            name: !isReordering ? null : 'flip-list'
          }"
          class="widgets-grid"
          item-key="id"
          :disabled="!isReordering"
          handle=".widget-title"
          :animation="200"
          ghost-class="widget-ghost"
          @update:model-value="handleListUpdate"
        >
          <template #item="{ element }">
            <div :class="['widget-item', store.state.widget.expandStates[element.id] ? 'expanded' : '']">
              <component :is="element.component" v-bind="element.props" />
            </div>
          </template>
        </VueDraggable>
      </v-container>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, computed, watch, onMounted, defineAsyncComponent, nextTick } from 'vue'
import { markRaw } from 'vue'
import VueDraggable from 'vuedraggable'
import { useStore } from 'vuex'
import { useCalendar } from '../composables/useCalendar'
import { useReport } from '../composables/useReport'
import { useWidgets } from '../composables/useWidgets'
import { getOrganization } from '../services/organizationService'
import { getReportStatus, getStatsData } from '../services/reportService'
import CalendarWidget from '../components/widget/CalendarWidget.vue'
import StatsWidget from '../components/widget/StatsWidget.vue'
import OrganizationWidget from '../components/widget/OrganizationWidget.vue'
import ReportRequestWidget from '../components/widget/ReportRequestWidget.vue'
import WeeklyReportWidget from '../components/widget/WeeklyReportWidget.vue'

const components = {
  CalendarWidget: markRaw(CalendarWidget),
  StatsWidget: markRaw(StatsWidget),
  OrganizationWidget: markRaw(OrganizationWidget),
  ReportRequestWidget: markRaw(ReportRequestWidget),
  WeeklyReportWidget: markRaw(WeeklyReportWidget),
  OvertimeChart: defineAsyncComponent(() => 
    import('../components/chart/OvertimeChart.vue').then(m => markRaw(m.default))
  ),
  StressChart: defineAsyncComponent(() => 
    import('../components/chart/StressChart.vue').then(m => markRaw(m.default))
  ),
  TodoListCard: defineAsyncComponent(() => 
    import('../components/widget/TodoListCard.vue').then(m => markRaw(m.default))
  )
}

const store = useStore()
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
const isLoading = ref(true)
const error = ref(null)
const isOvertimeDataReady = ref(false)
const isStressDataReady = ref(false)
const nextRequestDateTimeString = ref('')
const overtimeData = ref({ labels: [], datasets: [] })
const stressData = ref({ labels: [], datasets: [] })

const members = computed(() => organization.value?.members || [])
const weekString = computed(() => 
  weekIndex.value !== null ? getStringFromWeek(calendarWeeks[weekIndex.value]) : null
)
const filteredStatusOptions = computed(() => 
  statusOptions.filter(option => option.value !== 'all')
)

const reportStatus = ref({
  none: { count: 0, members: [] },
  pending: { count: 0, members: [] },
  inFeedback: { count: 0, members: [] },
  confirmed: { count: 0, members: [] },
  reportedCount: 0
})

const statusCounts = computed(() => ({
  none: reportStatus.value.none.count,
  pending: reportStatus.value.pending.count,
  feedback: reportStatus.value.inFeedback.count,
  approved: reportStatus.value.confirmed.count,
}))

const statusMembers = computed(() => ({
  none: reportStatus.value.none.members,
  pending: reportStatus.value.pending.members,
  feedback: reportStatus.value.inFeedback.members,
  approved: reportStatus.value.confirmed.members,
}))

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

const updateNextRequestDateTimeString = async () => {
  if (nextRequestDateTime.value) {
    nextRequestDateTimeString.value = formatFullDateTimeJp(nextRequestDateTime.value)
  } else {
    nextRequestDateTimeString.value = ''
  }
}

const fetchReportStatus = async () => {
  try {
    const status = await getReportStatus(organizationId, weekString.value)
    reportStatus.value = {
      ...status,
      reportedCount: status.pending.count + status.inFeedback.count + status.confirmed.count
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
    fill: false,
  })),
})

const getColor = (index) => {
  const colorPalette = [
    'rgb(96, 96, 255)', // 青
    'rgb(255, 159, 64)', // オレンジ
    'rgb(75, 192, 192)', // ターコイズ
    'rgb(153, 102, 255)', // 紫
    'rgb(255, 99, 132)', // ピンク
    'rgb(144, 238, 144)', // ライトグリーン
    'rgb(135, 206, 235)', // 水色
    'rgb(179, 183, 255)', // ライトラベンダー
    'rgb(255, 206, 86)', // 黄色
    'rgb(64, 224, 208)' // ターコイズブルー
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
      reportedCount: reportStatus.pending.count + reportStatus.inFeedback.count + reportStatus.confirmed.count
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
  fetchReportStatus()
  nextTick(() => {
    fetchSecondary()
  })
}

// Watchers
watch(weekIndex, fetchReportStatus)
watch(nextRequestDateTime, updateNextRequestDateTimeString, { immediate: true })

// Lifecycle hooks
onMounted(() => {
  weekIndex.value = calendarWeeks.length - 2// 先週
  fetchInitial()
  nextTick(() => {
    fetchSecondary()
  })
})

const expanded = computed(() => store.state.widget.expandStates['calendar'])

const { widgetOrder, isReordering, updateOrder } = useWidgets()

const sortableWidgets = computed(() => {
  if (!weekIndex.value) return []

  return widgetOrder.value.map(id => {
    const widgets = {
      calendar: markRaw({
        component: components.CalendarWidget,
        props: {
          calendarWeeks,
          weekIndex: weekIndex.value,
          'onUpdate:weekIndex': (v) => weekIndex.value = v,
          statusCounts: statusCounts.value,
          statusMembers: statusMembers.value,
          filteredStatusOptions: filteredStatusOptions.value,
          weekString: weekString.value
        }
      }),
      overtime: markRaw({
        component: components.StatsWidget,
        props: {
          widgetId: 'overtime',
          title: '残業時間の遷移（過去5週間）',
          chartComponent: components.OvertimeChart,
          chartData: overtimeData.value,
          isDataReady: isOvertimeDataReady.value
        }
      }),
      stress: markRaw({
        component: components.StatsWidget,
        props: {
          widgetId: 'stress',
          title: 'ストレス評価の遷移（過去5週間）',
          chartComponent: components.StressChart,
          chartData: stressData.value,
          isDataReady: isStressDataReady.value
        }
      }),
      organization: markRaw({
        component: components.OrganizationWidget,
        props: {
          organization: organization.value
        }
      }),
      reportRequest: markRaw({
        component: components.ReportRequestWidget,
        props: {
          organization: organization.value,
          nextRequestDateTime: nextRequestDateTime.value,
          nextRequestDateTimeString: nextRequestDateTimeString.value
        }
      }),
      todo: markRaw({
        component: components.TodoListCard,
        props: {}
      }),
      weeklyReport: markRaw({
        component: components.WeeklyReportWidget,
        props: {
          members: members.value,
          weekString: weekString.value,
          organizationId: organizationId
        }
      })
    }
    return markRaw({ id, ...widgets[id] })
  })
})

// リストの更新を処理
const handleListUpdate = (newList) => {
  updateOrder(newList.map(widget => widget.id))
}

// 初期化時の処理
onMounted(() => {
  weekIndex.value = calendarWeeks.length - 2 // 先週
  fetchInitial()
  nextTick(() => {
    fetchSecondary()
  })
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
  max-width: v-bind(expanded ? '560px' : '100%');
  margin: 0 auto;
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

.widget :deep(.v-card-title) {
  user-select: none;
}

.status-chip-wrapper {
  display: inline-block;
}

.widgets-container :deep(.v-col) {
  transition: all 0.3s ease;
}

.widget-ghost {
  opacity: 0.5;
}

.widgets-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  padding: 6px;
}

.widget-item {
  grid-column: auto / span 1;
  transition: all 0.3s ease;
}

.widget-item.expanded {
  grid-column: 1 / -1;
}

.widget-title {
  cursor: default;
}

.widget-item :deep(.v-card) {
  transition: box-shadow 0.3s ease;
}

/* 並び換えモード時のスタイル */
:deep(.widget-title) {
  cursor: move;
}

.widget-item:hover :deep(.v-card) {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}
</style>