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
      :report="report"
      @submit-report="handleSubmit"
    />
  </v-container>
</template>

<script>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import WeekSelector from '../components/WeekSelector.vue'
import ReportForm from '../components/ReportForm.vue'
import { useReport } from '../composables/useReport'
import { useCalendar } from '../composables/useCalendar'
import { submitReport } from '../utils/reportService'

export default {
  name: 'WeeklyReport',
  components: {
    WeekSelector,
    ReportForm
  },
  props: {
    organizationId: {
      type: String,
      default: null
    },
    memberUuid: {
      type: String,
      default: null
    },
    weekString: {
      type: String,
      default: null
    }
  },
  setup(props) {
    const { initialReport } = useReport()
    const { getWeekFromString, getStringFromWeek, isWeekInRange } = useCalendar()
    const router = useRouter()

    const report = ref(initialReport(props.organizationId, props.memberUuid, props.weekString))
    const selectedWeek = ref(null)
    const isValidWeek = ref(true)

    const handleWeekSelection = (week) => {
      selectedWeek.value = week;
      if (week && isWeekInRange(week)) {
        const weekString = getStringFromWeek(week);
        if (weekString) {
          Object.assign(report, initialReport(props.organizationId, props.memberUuid, weekString));
          router.push({
            name: 'WeeklyReport',
            params: { organizationId: props.organizationId, memberUuid: props.memberUuid, weekString }
          });
          isValidWeek.value = true;
        } else {
          isValidWeek.value = false;
        }
      } else {
        router.push({ 
          name: 'WeeklyReportSelector',
          params: { organizationId: props.organizationId, memberUuid: props.memberUuid }
         });
        isValidWeek.value = true;
      }
    }

    const handleReset = () => {
      selectedWeek.value = null;
      isValidWeek.value = true;
      router.push({ 
        name: 'WeeklyReportSelector',
        params: { organizationId: props.organizationId, memberUuid: props.memberUuid }
      });
    }

    const updateReport = (newReport) => {
      Object.assign(report, newReport);
    }

    const handleSubmit = async () => {
      try {
        const result = await submitReport(report);
        console.log('Report submitted successfully:', result);
        // 成功メッセージを表示するなどの処理を追加
      } catch (error) {
        console.error('Failed to submit report:', error);
        // エラーメッセージを表示するなどの処理を追加
      }
    }

    watch(() => props.weekString, (newWeekParam) => {
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