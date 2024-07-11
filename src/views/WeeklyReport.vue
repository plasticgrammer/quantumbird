<template>
  <v-container>
    <WeekSelector 
      :selectedWeek="selectedWeek"
      :isLocked="!!selectedWeek"
      @select-week="handleWeekSelection"
      @reset="handleReset"
    />

    <v-alert v-if="!isValidWeek" type="error" class="mt-5" outlined>
      指定された週は有効範囲外です。
    </v-alert>

    <ReportForm 
      v-if="showReportForm && isValidWeek" 
      :selectedWeek="selectedWeek"
      :report="report"
      @update:report="updateReport"
      @submit-report="handleSubmit"
    />
  </v-container>
</template>

<script>
import { ref, reactive, watch } from 'vue'
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
    const { getWeekFromString, getStringFromWeek, isWeekInRange } = useCalendar()
    const router = useRouter()

    const selectedWeek = ref(null)
    const report = reactive(initialReport())
    const showReportForm = ref(false)
    const isValidWeek = ref(true)

    const handleWeekSelection = (week) => {
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
      if (newWeekParam) {
        const week = getWeekFromString(newWeekParam);
        if (week && isWeekInRange(week)) {
          selectedWeek.value = week;
          setTimeout(() => {
            showReportForm.value = true;
          }, 700) // WeekSelectorのアニメーション時間に合わせて調整
          isValidWeek.value = true;
        } else {
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
      selectedWeek,
      handleWeekSelection,
      report,
      updateReport,
      handleSubmit,
      handleReset,
      showReportForm,
      isValidWeek
    }
  }
}
</script>