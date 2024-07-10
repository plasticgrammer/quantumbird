<template>
    <v-container>
      <WeekSelector
        :selected-week="selectedWeek"
        :is-locked="!!selectedWeek"
        @select-week="handleWeekSelection"
        @reset="handleReset"
      />
  
      <v-divider class="my-6"></v-divider>
  
      <template v-if="selectedWeek">
        <ReviewForm :reports="filteredReports" />
      </template>
      <v-alert v-else type="info" outlined>
        週を選択してレポートを表示してください。
      </v-alert>
    </v-container>
  </template>
  
  <script>
  import { ref, computed } from 'vue';
  import WeekSelector from './WeekSelector.vue';
  import ReviewForm from './ReviewForm.vue';
  
  export default {
    name: 'WeeklyReview',
    components: {
      WeekSelector,
      ReviewForm
    },
    setup() {
      const selectedWeek = ref(null);
      const allReports = ref([
        // ここに全てのレポートデータを入れます。
        // 例:
        {
          id: 1,
          name: "田中太郎",
          projects: [{ name: "プロジェクトA", tasks: "設計完了" }],
          overtime: 5,
          achievements: "設計完了",
          issues: "なし",
          improvements: "進捗を早める",
          status: "pending",
          weekStart: new Date('2024-07-08'),
        },
        // 他のレポートも同様に追加...
      ]);
  
      const filteredReports = computed(() => {
        if (!selectedWeek.value) return [];
        const startDate = selectedWeek.value[0];
        const endDate = selectedWeek.value[1];
        return allReports.value.filter(report => 
          report.weekStart >= startDate && report.weekStart <= endDate
        );
      });
  
      const handleWeekSelection = (week) => {
        selectedWeek.value = week;
      };
  
      const handleReset = () => {
        selectedWeek.value = null;
      };
  
      const formatDateRange = (week) => {
        if (!week || week.length < 2) return '';
        const start = week[0];
        const end = week[1];
        const options = { year: 'numeric', month: 'long', day: 'numeric' };
        return `${start.toLocaleDateString('ja-JP', options)} - ${end.toLocaleDateString('ja-JP', options)}`;
      };
  
      return {
        selectedWeek,
        filteredReports,
        handleWeekSelection,
        handleReset,
        formatDateRange
      };
    }
  };
  </script>
  
  <style scoped>
  /* 必要に応じてスタイルを追加 */
  </style>