<template>
  <v-card rounded="lg">
    <v-card-title class="d-flex align-center justify-space-between">
      <div class="d-flex align-center">
        <v-icon icon="mdi-magnify-scan" class="mr-2"></v-icon>
        活動分析
      </div>
      <v-btn
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
        <v-progress-circular indeterminate size="42" width="8" color="secondary"></v-progress-circular>
      </div>
      <template v-else>
        <div v-if="error" class="text-error">
          {{ error }}
        </div>
        <div v-else-if="!summary && !insights.length" class="text-subtitle-1 text-medium-emphasis text-center py-4">
          ボタンをクリックして分析レポートを生成してください
        </div>
        <div v-else class="px-4">
          <div class="text-h6 mb-2">全体の要約</div>
          <p class="text-body-1 px-1">{{ summary }}</p>
          
          <v-divider class="my-4"></v-divider>
          
          <template v-if="insights.positive.length">
            <div class="text-subtitle-1 font-weight-medium mt-2 mb-1">
              <v-icon color="success" class="mr-1">mdi-check-circle</v-icon>
              良好な点
            </div>
            <v-list density="compact" class="pt-0">
              <v-list-item
                v-for="(insight, index) in insights.positive"
                :key="'p'+index"
                class="px-2 py-1"
              >
                <v-list-item-title class="text-wrap d-flex align-center">
                  <v-icon icon="mdi-circle-small"></v-icon>
                  <span class="flex-grow-1">{{ insight.text }}</span>
                  <v-chip
                    size="small"
                    :color="getScoreColor(insight.score)"
                    class="ml-2"
                  >
                    {{ formatScore(insight.score) }}
                  </v-chip>
                </v-list-item-title>
              </v-list-item>
            </v-list>
          </template>
          
          <template v-if="insights.negative.length">
            <div class="text-subtitle-1 font-weight-medium mt-3 mb-1">
              <v-icon color="warning" class="mr-1">mdi-alert</v-icon>
              注意点・課題
            </div>
            <v-list density="compact" class="pt-0">
              <v-list-item
                v-for="(insight, index) in insights.negative"
                :key="'n'+index"
                class="px-2 py-1"
              >
                <v-list-item-title class="text-wrap d-flex align-center">
                  <v-icon icon="mdi-circle-small"></v-icon>
                  <span class="flex-grow-1">{{ insight.text }}</span>
                  <v-chip
                    size="small"
                    :color="getScoreColor(insight.score)"
                    class="ml-2"
                  >
                    {{ formatScore(insight.score) }}
                  </v-chip>
                </v-list-item-title>
              </v-list-item>
            </v-list>
          </template>
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
    const result = await getWeeklyReportSummary(props.reports)
    summary.value = result.summary
    insights.value = result.insights
    
    if (!summary.value && !insights.value?.positive?.length && !insights.value?.negative?.length) {
      error.value = 'サマリーの生成に失敗しました'
    }
  } catch (err) {
    error.value = err.message || 'サマリーの生成に失敗しました'
    console.error('Summary generation error:', err)
  } finally {
    loading.value = false
  }
}

const formatScore = (score) => {
  return score ? score.toFixed(0) : '0'
}

const getScoreColor = (score) => {
  if (score >= 90) return 'error'
  /*
  if (score >= 70) return 'warning'
  if (score >= 50) return 'info'
  return 'success'
  */
  return 'grey'
}
</script>

<style scoped>
.text-wrap {
  white-space: normal;
  word-break: break-word;
  line-height: 1.6;
}
</style>
