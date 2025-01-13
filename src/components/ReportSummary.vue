<template>
  <v-card rounded="lg" class="mb-4">
    <v-card-title class="d-flex align-center justify-space-between">
      <div class="d-flex align-center">
        <v-icon icon="mdi-lightbulb" class="mr-2"></v-icon>
        サマリー
      </div>
      <v-btn
        :loading="loading"
        :disabled="!hasValidReports || loading"
        color="secondary"
        variant="tonal"
        @click="generateSummary"
      >
        <v-icon
          icon="mdi-auto-fix"
          size="20"
          class="mr-1"
        ></v-icon>
        {{ summary ? '再分析' : 'AI分析' }}
      </v-btn>
    </v-card-title>
    <v-card-text>
      <div v-if="loading" class="d-flex align-center justify-center py-4">
        <v-progress-circular indeterminate></v-progress-circular>
      </div>
      <template v-else>
        <div v-if="error" class="text-error">
          {{ error }}
        </div>
        <div v-else-if="!summary && !insights.length" class="text-subtitle-1 text-medium-emphasis text-center py-4">
          ボタンをクリックしてサマリーを生成してください
        </div>
        <div v-else>
          <div class="text-h6 mb-2">活動の概要</div>
          <p class="text-body-1">{{ summary }}</p>
          
          <v-divider class="my-4"></v-divider>
          
          <div class="text-h6 mb-2">主要なインサイト</div>
          <v-list>
            <v-list-item
              v-for="(insight, index) in insights"
              :key="index"
              class="px-0 py-2"
            >
              <template #prepend>
                <v-icon color="primary" class="mt-1">mdi-chart-line</v-icon>
              </template>
              <v-list-item-title class="text-wrap">
                {{ insight }}
              </v-list-item-title>
            </v-list-item>
          </v-list>
        </div>
      </template>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref, computed } from 'vue'
import { getWeeklyReportSummary } from '@/services/bedrockService'

const props = defineProps({
  reports: {
    type: Array,
    required: true
  }
})

const loading = ref(false)
const error = ref(null)
const summary = ref('')
const insights = ref([])

// 有効なレポートがあるかチェック
const hasValidReports = computed(() => {
  return props.reports.some(report => 
    report.report && 
    report.report.status !== 'none' &&
    report.report.projects?.length > 0
  )
})

const generateSummary = async () => {
  if (!hasValidReports.value) {
    error.value = '有効な週次報告がありません'
    return
  }
  
  loading.value = true
  error.value = null
  
  try {
    const { summary: summaryText, insights: insightsList } = await getWeeklyReportSummary(props.reports)
    summary.value = summaryText
    insights.value = insightsList
    
    if (!summary.value && !insights.value.length) {
      error.value = 'サマリーの生成に失敗しました'
    }
  } catch (err) {
    error.value = err.message || 'サマリーの生成に失敗しました'
    console.error('Summary generation error:', err)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.text-wrap {
  white-space: normal;
  word-break: break-word;
  line-height: 1.6;
}
</style>
