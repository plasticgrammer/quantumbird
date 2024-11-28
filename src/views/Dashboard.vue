<template>
  <v-container>
    <v-row dense class="pb-2">
      <v-col cols="6">
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
      <v-col cols="6" class="d-flex justify-end align-center pe-3">
        <v-menu 
          v-model="isMenuOpen"
          :close-on-content-click="false"
        >
          <template #activator="{ props }">
            <v-btn
              v-tooltip="'ウィジェットの表示設定'"
              v-bind="props"
              icon="mdi-cog"
              aria-label="ウィジェット設定"
              class="opacity-80 mr-2"
              density="comfortable"
            ></v-btn>
          </template>
          <v-list class="rounded-lg">
            <v-list-subheader>表示するウィジェット</v-list-subheader>
            <v-list-item 
              v-for="(def, id) in WIDGET_DEFINITIONS" 
              :key="id" 
              class="px-5"
              @click.stop="handleVisibilityChange(id)"
            >
              <v-list-item-title class="text-body-2">{{ def.title }}</v-list-item-title>
              <template #append>
                <v-switch
                  :model-value="store.state.widget.widgetVisibility[id]"
                  hide-details
                  inset
                  density="compact"
                  color="primary"
                ></v-switch>
              </template>
            </v-list-item>
          </v-list>
        </v-menu>
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
          v-model="currentWidgets"
          :component-data="{
            tag: 'div',
            type: 'transition-group',
            name: !isLoading ? 'flip-list' : null
          }"
          class="widgets-grid"
          item-key="id"
          handle=".widget-title"
          :animation="200"
          ghost-class="widget-ghost"
          :disabled="isLoading"
        >
          <template #item="{ element }">
            <div 
              :class="[
                'widget-item', 
                { 'expanded': isMobile || expandStates[element.id] }
              ]"
            >
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
import OrganizationWidget from '../components/widget/OrganizationWidget.vue'
import ReportRequestWidget from '../components/widget/ReportRequestWidget.vue'
import WeeklyReportWidget from '../components/widget/WeeklyReportWidget.vue'
import { useResponsive } from '../composables/useResponsive'

const components = {
  CalendarWidget: markRaw(CalendarWidget),
  OrganizationWidget: markRaw(OrganizationWidget),
  ReportRequestWidget: markRaw(ReportRequestWidget),
  WeeklyReportWidget: markRaw(WeeklyReportWidget),
  OvertimeChart: defineAsyncComponent(() => 
    import('../components/chart/OvertimeChart.vue').then(m => markRaw(m.default))
  ),
  StressChart: defineAsyncComponent(() => 
    import('../components/chart/StressChart.vue').then(m => markRaw(m.default))
  ),
  DisabilityChart: defineAsyncComponent(() => 
    import('../components/chart/DisabilityChart.vue').then(m => markRaw(m.default))
  ),
  AchievementChart: defineAsyncComponent(() => 
    import('../components/chart/AchievementChart.vue').then(m => markRaw(m.default))
  ),
  TodoListWidget: defineAsyncComponent(() => 
    import('../components/widget/TodoListWidget.vue').then(m => markRaw(m.default))
  )
}

const store = useStore()
const { createWeeks, getStringFromWeek, formatFullDateTimeJp } = useCalendar()
const { statusOptions } = useReport()
const { isMobile } = useResponsive()

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
const isDisabilityDataReady = ref(false)
const isAchievementDataReady = ref(false)
const nextRequestDateTimeString = ref('')
const overtimeData = ref({ labels: [], datasets: [] })
const stressData = ref({ labels: [], datasets: [] })
const disabilityData = ref({ labels: [], datasets: [] })
const achievementData = ref({ labels: [], datasets: [] })

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
    disabilityData.value = formatChartData(statsData, 'disability')
    achievementData.value = formatChartData(statsData, 'achievement')
    isOvertimeDataReady.value = true
    isStressDataReady.value = true
    isDisabilityDataReady.value = true
    isAchievementDataReady.value = true
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

// ウィジェット関連の設定をより宣言的に
const { 
  WIDGET_DEFINITIONS,
  getWidgetComponent,
  visibleWidgets,
  expandStates,
  updateOrder
} = useWidgets()

const getWidgetProps = (id) => {
  const propConfigs = {
    calendar: () => ({
      calendarWeeks,
      weekIndex: weekIndex.value,
      'onUpdate:weekIndex': (v) => weekIndex.value = v,
      statusCounts: statusCounts.value,
      statusMembers: statusMembers.value,
      filteredStatusOptions: filteredStatusOptions.value,
      weekString: weekString.value
    }),
    overtime: () => createChartProps('overtime', overtimeData.value, isOvertimeDataReady.value),
    stress: () => createChartProps('stress', stressData.value, isStressDataReady.value),
    disability: () => createChartProps('disability', disabilityData.value, isDisabilityDataReady.value),
    achievement: () => createChartProps('achievement', achievementData.value, isAchievementDataReady.value),
    organization: () => ({ organization: organization.value }),
    reportRequest: () => ({
      organization: organization.value,
      nextRequestDateTime: nextRequestDateTime.value,
      nextRequestDateTimeString: nextRequestDateTimeString.value
    }),
    todo: () => ({}),
    weeklyReport: () => ({
      members: members.value,
      weekString: weekString.value,
      organizationId
    })
  }

  return (propConfigs[id] || (() => ({})))()
}

const createChartProps = (widgetId, chartData, isDataReady) => ({
  widgetId,
  title: WIDGET_DEFINITIONS[widgetId].title,
  chartData,
  isDataReady
})

const currentWidgets = computed({
  get: () => {
    return visibleWidgets.value.map(id => ({
      id,
      component: components[getWidgetComponent(id)],
      props: getWidgetProps(id)
    }))
  },
  set: (newList) => {
    if (newList?.length) {
      updateOrder(newList.map(item => item.id))
    }
  }
})

onMounted(() => {
  weekIndex.value = calendarWeeks.length - 2 // 先週
  fetchInitial()
  nextTick(() => {
    fetchSecondary()
  })
})

const isMenuOpen = ref(false)

const handleVisibilityChange = (id) => {
  store.dispatch('widget/toggleWidgetVisibility', id)
}
</script>

<style scoped>
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

/* 常に並び換え可能な状態を示すスタイル */
:deep(.widget-title) {
  cursor: move;
}

.widget-item:hover :deep(.v-card) {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}
</style>