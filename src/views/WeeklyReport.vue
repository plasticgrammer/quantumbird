<template>
  <div class="weekly-report-container">
    <WeekSelector 
      :calendarWeeks="calendarWeeks"
      :selectedWeek="selectedWeek"
      :isLocked="isLocked"
      @select-week="selectWeek"
      @reset="handleReset"
    />

    <div v-if="!isValidWeek" class="error-message">
      指定された週は有効範囲外です。
    </div>

    <ReportForm 
      v-if="showReportForm && isValidWeek" 
      :selectedWeek="selectedWeek"
      :report="report"
      @update:report="updateReport"
      @submit-report="handleSubmit"
    />
  </div>
</template>

<script>
import { ref, reactive, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import WeekSelector from '../components/WeekSelector.vue'
import ReportForm from '../components/ReportForm.vue'
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
    const { initialReport } = useReport()
    const { calendarWeeks, getWeekFromString, getStringFromWeek, getWeekNumber } = useCalendar()
    const router = useRouter()

    const selectedWeek = ref(null)
    const report = reactive(initialReport())
    const showReportForm = ref(false)
    const isValidWeek = ref(true)

    const isLocked = computed(() => !!selectedWeek.value)

    const calendarDateRange = computed(() => {
      if (calendarWeeks.value.length === 0) return { start: null, end: null };
      const start = calendarWeeks.value[0][0];
      const end = calendarWeeks.value[calendarWeeks.value.length - 1][6];
      return { start, end };
    });

    const isWeekInRange = (week) => {
      if (!week || !calendarDateRange.value.start || !calendarDateRange.value.end) return false;
      return getWeekNumber(week[0]) >= getWeekNumber(calendarDateRange.value.start) 
        && getWeekNumber(week[1]) <= getWeekNumber(calendarDateRange.value.end);
    };

    const selectWeek = (week) => {
      console.log('selectWeek called with:', week);
      selectedWeek.value = week;
      if (week && isWeekInRange(week)) {
        const weekString = getStringFromWeek(week);
        if (weekString) {
          router.push(`/report/${weekString}`);
          setTimeout(() => {
            showReportForm.value = true;
          }, 700) // WeekSelectorのアニメーション時間に合わせて調整
          isValidWeek.value = true;
        } else {
          console.error('Failed to generate week string');
          showReportForm.value = false;
          isValidWeek.value = false;
        }
      } else {
        router.push('/report');
        showReportForm.value = false;
        isValidWeek.value = true;
      }
    }

    const handleReset = () => {
      console.log('Handling reset');
      showReportForm.value = false;
      selectedWeek.value = null;
      isValidWeek.value = true;
      router.push('/report');
    }

    const updateReport = (newReport) => {
      Object.assign(report, newReport);
    }

    const handleSubmit = () => {
      console.log('Report submitted:', report);
      // ここで報告の送信処理を実装します
      // 例: submitReport(report);
    }

    watch(() => props.weekParam, (newWeekParam) => {
      console.log('Week param changed:', newWeekParam);
      if (newWeekParam) {
        const week = getWeekFromString(newWeekParam);
        if (week && isWeekInRange(week)) {
          selectedWeek.value = week;
          setTimeout(() => {
            showReportForm.value = true;
          }, 700) // WeekSelectorのアニメーション時間に合わせて調整
          isValidWeek.value = true;
        } else {
          console.error('Invalid or out of range week parameter:', newWeekParam);
          selectedWeek.value = null;
          showReportForm.value = false;
          isValidWeek.value = false;
        }
      } else {
        selectedWeek.value = null;
        showReportForm.value = false;
        isValidWeek.value = true;
      }
    }, { immediate: true })

    return {
      calendarWeeks,
      selectedWeek,
      selectWeek,
      report,
      updateReport,
      handleSubmit,
      showReportForm,
      handleReset,
      isValidWeek,
      isLocked
    }
  }
}
</script>

<style scoped>
.weekly-report-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 10px 0;
}

.error-message {
  color: red;
  margin-top: 10px;
}
</style>