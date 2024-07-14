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

    <ReportForm v-if="selectedWeek && isValidWeek" 
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

    const report = reactive(initialReport())
    const selectedWeek = ref(null)
    const isValidWeek = ref(true)

    const handleWeekSelection = (week) => {
      selectedWeek.value = week;
      if (week && isWeekInRange(week)) {
        const weekString = getStringFromWeek(week);
        if (weekString) {
          router.push({
            name: 'WeekReportSelector',
            params: { weekParam: weekString }
          });
          isValidWeek.value = true;
        } else {
          isValidWeek.value = false;
        }
      } else {
        router.push({ name: 'WeekReportSelector' });
        isValidWeek.value = true;
      }
    }

    const handleReset = () => {
      selectedWeek.value = null;
      isValidWeek.value = true;
      router.push({ name: 'WeekReportSelector' });
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
          isValidWeek.value = true;
        } else {
          selectedWeek.value = null;
          isValidWeek.value = false;
        }
      } else {
        selectedWeek.value = null;
        isValidWeek.value = true;
      }
    }, { immediate: true })

    return {
      report,
      selectedWeek,
      isValidWeek,
      handleWeekSelection,
      updateReport,
      handleSubmit,
      handleReset,
    }
  }
}
</script>