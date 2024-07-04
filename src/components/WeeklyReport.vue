<template>
  <div class="weekly-report-container" :style="containerStyle">
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
    const containerHeight = ref('auto')

    const isLocked = computed(() => selectedWeek.value !== null && showReportForm.value)

    const containerStyle = computed(() => ({
      height: containerHeight.value,
      overflow: 'hidden'
    }))

    const selectWeek = (week) => {
      selectedWeek.value = week
      if (week) {
        // コンテナの高さを固定
        containerHeight.value = `${document.querySelector('.weekly-report-container').offsetHeight}px`
        setTimeout(() => {
          showReportForm.value = true
          // アニメーション完了後、高さを自動に戻す
          setTimeout(() => {
            containerHeight.value = 'auto'
          }, 300)
        }, 800) // WeekSelectorのアニメーション時間に合わせて調整
      } else {
        showReportForm.value = false
      }
    }

    const handleReset = async () => {
      // コンテナの高さを固定
      containerHeight.value = `${document.querySelector('.weekly-report-container').offsetHeight}px`
      
      // ReportForm を非表示にする
      showReportForm.value = false
      
      // ReportForm のフェードアウトアニメーションが完了するのを待つ
      await new Promise(resolve => setTimeout(resolve, 300))
      
      // 週選択をリセット
      selectedWeek.value = null
      
      // アニメーション完了後、高さを自動に戻す
      setTimeout(() => {
        containerHeight.value = 'auto'
      }, 500) // 週選択のアニメーション時間に合わせて調整
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
      handleSubmit,
      showReportForm,
      isLocked,
      handleReset,
      containerStyle
    }
  }
}
</script>

<style scoped>
.weekly-report-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  transition: height 0.5s ease-out;
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