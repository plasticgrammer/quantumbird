<template>
  <div class="weekly-report-container">
    <WeekSelector 
      :calendarWeeks="calendarWeeks"
      :selectedWeek="selectedWeek"
      @select-week="selectWeek"
    />

    <transition name="fade">
      <ReportForm 
        v-if="showReportForm" 
        :selectedWeek="selectedWeek"
        :report="report"
        @update:report="updateReport"
        @submit-report="handleSubmit"
      />
    </transition>
  </div>
</template>

<script>
import { ref, reactive, watch } from 'vue'
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

    const selectWeek = (week) => {
      selectedWeek.value = week
      if (week) {
        setTimeout(() => {
          showReportForm.value = true
        }, 800) // WeekSelectorのアニメーション時間に合わせて調整
      } else {
        showReportForm.value = false
      }
    }

    const updateReport = (newReport) => {
      Object.assign(report, newReport)
    }

    const handleSubmit = () => {
      console.log('Submitted report:', report)
      submitReport(report)
      // ここで追加の送信処理を実装できます
    }

    watch(selectedWeek, (newValue) => {
      if (!newValue) {
        showReportForm.value = false
      }
    })

    return {
      calendarWeeks,
      selectedWeek,
      selectWeek,
      report,
      updateReport,
      handleSubmit,
      showReportForm
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

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>