<template>
  <div class="weekly-report-container">
    <WeekSelector 
      :calendarWeeks="calendarWeeks"
      :selectedWeek="selectedWeek"
      @select-week="selectWeek"
    />

    <ReportForm 
      v-if="selectedWeek" 
      :selectedWeek="selectedWeek"
      :report="report"
      @update:report="updateReport"
      @submit-report="handleSubmit"
    />
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
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
  setup() {
    const { initialReport, submitReport } = useReport()
    const { calendarWeeks } = useCalendar()

    const selectedWeek = ref(null)
    const report = reactive(initialReport())

    const selectWeek = (week) => {
      selectedWeek.value = week
    }

    const updateReport = (newReport) => {
      Object.assign(report, newReport)
    }

    const handleSubmit = () => {
      console.log('Submitted report:', report)
      submitReport(report)
      // ここで追加の送信処理を実装できます
    }

    return {
      calendarWeeks,
      selectedWeek,
      selectWeek,
      report,
      updateReport,
      handleSubmit
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