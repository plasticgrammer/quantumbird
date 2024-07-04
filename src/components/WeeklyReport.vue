<template>
  <div class="weekly-report-container">
    <WeekSelector 
      :calendarWeeks="calendarWeeks"
      :selectedWeek="selectedWeek"
      :isLocked="isLocked"
      @select-week="selectWeek"
      @reset="handleReset"
    />

    <ReportForm 
      v-if="showReportForm" 
      :selectedWeek="selectedWeek"
      :report="report"
      @update:report="updateReport"
      @submit-report="handleSubmit"
    />
  </div>
</template>

<script>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import WeekSelector from './WeekSelector.vue'
import ReportForm from './ReportForm.vue'
import { useReport } from '../composables/useReport'
import { useCalendar } from '../composables/useCalendar'

export default {
  name: 'WeeklyReport',
  components: {
    WeekSelector,
    ReportForm
  },
  props: {
    weekParam: {
      type: String,
      default: null
    }
  },
  setup(props) {
    const { initialReport, submitReport } = useReport()
    const { calendarWeeks, getWeekFromString, getStringFromWeek } = useCalendar()
    const router = useRouter()
    const route = useRoute()

    const selectedWeek = ref(null)
    const report = reactive(initialReport())
    const showReportForm = ref(false)

    const isLocked = computed(() => selectedWeek.value !== null && showReportForm.value)

    const selectWeek = (week) => {
      selectedWeek.value = week
      if (week) {
        const weekString = getStringFromWeek(week)
        router.push({ query: { week: weekString } })
        setTimeout(() => {
          showReportForm.value = true
        }, 500)
      } else {
        router.push({ query: {} })
        showReportForm.value = false
      }
    }

    const handleReset = () => {
      showReportForm.value = false
      setTimeout(() => {
        selectedWeek.value = null
        router.push({ query: {} })
      }, 100)
    }

    // URLパラメータが変更されたときの処理
    watch(() => route.query.week, (newWeek) => {
      if (newWeek) {
        const week = getWeekFromString(newWeek)
        if (week) {
          selectedWeek.value = week
          showReportForm.value = true
        }
      } else {
        selectedWeek.value = null
        showReportForm.value = false
      }
    })

    // コンポーネントのマウント時にURLパラメータを確認
    onMounted(() => {
      if (props.weekParam) {
        const week = getWeekFromString(props.weekParam)
        if (week) {
          selectedWeek.value = week
          showReportForm.value = true
        }
      }
    })

    const updateReport = (newReport) => {
      Object.assign(report, newReport)
    }

    const handleSubmit = () => {
      console.log('Submitted report:', report)
      submitReport(report)
    }

    return {
      calendarWeeks,
      selectedWeek,
      selectWeek,
      report,
      updateReport,
      handleSubmit,
      showReportForm,
      isLocked,
      handleReset
    }
  }
}
</script>

<style scoped>
.weekly-report-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}
</style>