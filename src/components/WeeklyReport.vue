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
import { ref, reactive, computed } from 'vue'
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
    const showReportForm = ref(false)

    const isLocked = computed(() => selectedWeek.value !== null && showReportForm.value)

    const selectWeek = (week) => {
      selectedWeek.value = week
      if (week) {
        // WeekSelectorのアニメーション完了後にReportFormを表示
        setTimeout(() => {
          showReportForm.value = true
        }, 700) // アニメーション時間に合わせて調整
      } else {
        showReportForm.value = false
      }
    }

    const handleReset = () => {
      // まずReportFormを非表示にする
      showReportForm.value = false
      // 少し遅延を入れてから週選択をリセット
      setTimeout(() => {
        selectedWeek.value = null
      }, 100)
    }

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