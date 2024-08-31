<template>
  <v-container class="review-form-container">
    <v-row 
      v-if="reports.length && !readonly"
      class="d-print-none mt-2"
    >
      <v-col cols="12" md="10" class="py-0">
        <v-card
          class="px-2 align-center bg-transparent"
          elevation="0"
        >
          <v-chip-group
            v-model="selectedStatus"
            column
          >
            <span 
              v-for="status in statusOptions"
              :key="status.value"
            >
              <v-chip
                v-if="statusCounts[status.value] > 0"
                :value="status.value"
                :color="status.color"
                outlined
                filter
              >
                {{ status.text }}: {{ statusCounts[status.value] }}
              </v-chip>
            </span>
          </v-chip-group>
        </v-card>
      </v-col>
      <v-col cols="12" md="2" class="text-end">
        <v-btn
          color="secondary"
          size="small"
          @click="copyShareUrl"
        >
          <v-icon class="mr-2">
            mdi-share-variant
          </v-icon>
          共有する
        </v-btn>
      </v-col>
    </v-row>

    <v-row v-if="isLoading">
      <v-col v-for="i in 3" :key="i" cols="12">
        <v-skeleton-loader
          type="avatar, text, ossein, paragraph, text, actions"
          :loading="true"
          elevation="4"
          class="mt-2"
        ></v-skeleton-loader>
      </v-col>
    </v-row>
    <v-row v-else>
      <v-col
        v-for="report in filteredReports"
        :key="report.memberUuid"
        cols="12"
      >
        <v-card
          :class="{ 'approved-card': report.status === 'approved', 'none-card': report.status === 'none' }"
          class="cursor-default mt-2"
          hover
          outlined
        >
          <v-card-title class="d-flex justify-space-between align-center py-2">
            <span class="text-h6 font-weight-bold">
              <v-icon size="x-large" class="mr-1">
                mdi-account-box-outline
              </v-icon>
              {{ report.name }}
            </span>
            <v-chip
              :color="getStatusColor(report.status)"
              label
              x-small
              class="status-chip ml-2"
            >
              <v-icon
                v-if="report.status === 'approved'"
                class="mr-1"
                x-small
              >
                mdi-check-circle-outline
              </v-icon>
              {{ getStatusText(report.status) }}
            </v-chip>
          </v-card-title>

          <v-card-text
            v-if="report.status !== 'none'"
            class="pa-4" 
          >
            <v-row>
              <v-col
                cols="12"
                md="5"
                class="d-flex flex-column"
              >
                <div class="text-subtitle-1 font-weight-medium mb-1">
                  作業内容
                </div>
                <v-list
                  dense
                  class="tasks pa-0 mb-3"
                >
                  <v-list-item
                    v-for="(project, index) in report.projects"
                    :key="index"
                    class="px-2 py-2"
                  >
                    <v-list-item-title>
                      <v-icon small>
                        mdi-folder-outline
                      </v-icon>
                      {{ project.name }}
                    </v-list-item-title>
                    <v-list-item-subtitle class="d-block ml-2 my-2">
                      <ul class="work-items-list">
                        <li v-for="(item, itemIndex) in project.workItems" :key="itemIndex">
                          {{ item.content }}
                        </li>
                      </ul>
                    </v-list-item-subtitle>
                  </v-list-item>
                </v-list>
                <div class="mt-auto">
                  <v-chip
                    color="primary"
                    x-small
                  >
                    <v-icon
                      class="mr-1"
                      x-small
                    >
                      mdi-clock-outline
                    </v-icon>
                    残業: {{ report.overtime }}時間
                  </v-chip>
                </div>
              </v-col>
              <v-col
                cols="12"
                md="7"
              >
                <div class="text-subtitle-1 font-weight-medium mb-1">
                  現状と問題点
                </div>
                <v-textarea
                  v-model="report.issues"
                  outlined
                  readonly
                  auto-grow
                  rows="2"
                  hide-details
                  class="small-text-area mb-2"
                />

                <div class="text-subtitle-1 font-weight-medium mb-1">
                  改善したいこと
                </div>
                <v-textarea
                  v-model="report.improvements"
                  outlined
                  readonly
                  auto-grow
                  rows="1"
                  hide-details
                  class="small-text-area"
                />
              </v-col>
            </v-row>

            <v-card 
              class="mt-4 border-sm"
              elevation="2"
              variant="flat"
              color="light-blue-lighten-5"
              title="評価"
            >
              <template #prepend>
                <v-icon icon="mdi-poll"></v-icon>
              </template>
              <v-card-text>
                <rating-item
                  v-for="item in ratingItems"
                  :key="item.key"
                  v-model="report.rating[item.key]"
                  :label="item.label"
                  :item-labels="item.itemLabels"
                  :negative="item.negative"
                  :readonly="true"
                />
              </v-card-text>
            </v-card>

            <v-row class="mt-2">
              <v-col cols="12">
                <v-alert
                  v-if="report.feedbacks.length" 
                  density="compact"
                  border="start"
                  border-color="warning"
                  elevation="2"
                  outlined
                  dense
                  class="px-2 mb-3"
                  color="white"
                >
                  <div
                    v-for="(feedback, index) in report.feedbacks" :key="index"
                    class="pa-0"
                  >
                    <v-textarea
                      v-model="feedback.content"
                      :label="`${ new Date(feedback.createdAt).toLocaleString() }`"
                      readonly
                      rows="1"
                      auto-grow
                      hide-details
                      density="comfortable"
                      class="borderless-textarea"
                    >
                      <template #prepend-inner>
                        <v-icon class="mr-1" color="orange">
                          mdi-reply
                        </v-icon>
                      </template>
                    </v-textarea>
                    <v-textarea
                      v-if="!!feedback.replyComment"
                      v-model="feedback.replyComment"
                      label="返信コメント"
                      readonly
                      rows="1"
                      auto-grow
                      hide-details
                      density="comfortable"
                      class="ml-8 mt-n2 borderless-textarea"
                    >
                      <template #prepend-inner>
                        <v-icon size="large" class="mr-1" color="grey">
                          mdi-message
                        </v-icon>
                      </template>
                    </v-textarea>
                  </div>
                </v-alert>

                <v-textarea
                  v-if="report.status !== 'approved' && !readonly"
                  v-model="newFeedback"
                  label="新しいフィードバックを入力..."
                  outlined
                  dense
                  class="d-print-none"
                  clear-icon="mdi-close-circle"
                  clearable 
                  hide-details="auto"
                  rows="2"
                >
                  <template #prepend-inner>
                    <v-icon size="large" class="mr-1" color="grey">
                      mdi-reply
                    </v-icon>
                  </template>
                </v-textarea>
              </v-col>
            </v-row>
          </v-card-text>

          <v-card-actions
            v-if="report.status !== 'approved' && report.status !== 'none' && !readonly"
            class="d-print-none pt-0 pb-3"
          >
            <v-spacer />
            <v-btn
              color="primary"
              variant="elevated" 
              outlined
              x-small
              @click="handleApprove(report.memberUuid)"
            >
              <v-icon left x-small class="mr-1">
                mdi-check-bold
              </v-icon>
              確認済み
            </v-btn>
            <v-btn
              color="warning"
              variant="elevated" 
              :disabled="!newFeedback.trim()"
              class="ml-2"
              outlined
              x-small
              @click="handleFeedback(report.memberUuid)"
            >
              <v-icon left x-small class="mr-1">
                mdi-reply
              </v-icon>
              フィードバック送信
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, computed, watchEffect, onMounted, inject } from 'vue'
import { useReport } from '../composables/useReport'
import { listReports, listMembers } from '../services/publicService'
import { updateReport, submitFeedback } from '../services/reportService'
import { generateToken } from '../services/secureParameterService'
import RatingItem from '../components/RatingItem.vue'

const { statusOptions, getStatusText, getStatusColor, ratingItems } = useReport()
const showNotification = inject('showNotification')

const props = defineProps({
  organizationId: {
    type: String,
    required: true
  },
  weekString: {
    type: String,
    required: true
  },
  readonly: {
    type: Boolean,
    default: false
  }
})

const reports = ref([])
const isLoading = ref(true)
const error = ref(null)
const newFeedback = ref('')

const selectedStatus = ref('all')

// watchをwatchEffectに変更
watchEffect(() => {
  if (selectedStatus.value === undefined) {
    selectedStatus.value = 'all'
  }
})

// メモ化されたステータスカウントを最適化
const statusCounts = computed(() => {
  return reports.value.reduce((counts, report) => {
    counts[report.status]++
    return counts
  }, { all: reports.value.length, none: 0, pending: 0, feedback: 0, approved: 0 })
})

// メモ化されたフィルタリングを最適化
const filteredReports = computed(() => 
  selectedStatus.value === 'all' 
    ? reports.value 
    : reports.value.filter(report => report.status === selectedStatus.value)
)

// copyShareUrl メソッドを最適化
const copyShareUrl = async () => {
  try {
    const params = { organizationId: props.organizationId, weekString: props.weekString }
    const result = await generateToken(params)
    
    const rootUrl = window.location.origin
    const shareUrl = `${rootUrl}/view/${result.token}`
    
    await navigator.clipboard.writeText(shareUrl)
    showNotification('コピーに成功しました')
  } catch (err) {
    console.error('Failed to copy share URL:', err)
    showNotification('コピーに失敗しました', 'error')
  }
}

const fetchReports = async () => {
  try {
    const fetchedReports = await listReports(props.organizationId, props.weekString)
    
    if (!fetchedReports) {
      console.error('No reports data received')
      return []
    }

    if (!Array.isArray(fetchedReports)) {
      console.error('Fetched reports is not an array:', fetchedReports)
      return []
    }

    return fetchedReports.map(report => {
      if (!report || typeof report !== 'object') {
        console.error('Invalid report object:', report)
        return null
      }

      return {
        ...report,
        projects: Array.isArray(report.projects)
          ? report.projects.map(project => ({
            name: project.name,
            workItems: Array.isArray(project.workItems)
              ? project.workItems
              : [],
          }))
          : [],
        feedbacks: Array.isArray(report.feedbacks) ? report.feedbacks : [],
        status: report.status || 'pending',
      }
    }).filter(report => report !== null)
  } catch (err) {
    console.error('Failed to fetch reports:', err)
    throw new Error(`Failed to fetch reports: ${err.message}`)
  }
}

const fetchMembers = async () => {
  try {
    return await listMembers(props.organizationId)
  } catch (err) {
    console.error('Failed to fetch members:', err)
    throw err
  }
}

// fetchData メソッドを最適化
const processReports = (fetchedReports, members) => {
  const statusOrder = { none: 0, pending: 1, feedback: 2, approved: 3 }
  
  return members.map(member => {
    const report = fetchedReports.find(r => r.memberUuid === member.memberUuid) || {}
    return {
      memberUuid: member.memberUuid,
      weekString: props.weekString,
      organizationId: props.organizationId,
      memberId: member.id,
      name: member.name,
      projects: report.projects || [],
      overtime: report.overtime || 0,
      achievements: report.achievements || '',
      issues: report.issues || '',
      improvements: report.improvements || '',
      rating: report.rating || {},
      status: report.status || 'none',
      feedbacks: report.feedbacks || [],
      approvedAt: report.approvedAt || null
    }
  }).sort((a, b) => {
    if (a.status === b.status) return a.memberId.localeCompare(b.memberId)
    return (statusOrder[a.status] ?? Number.MAX_SAFE_INTEGER) - (statusOrder[b.status] ?? Number.MAX_SAFE_INTEGER)
  })
}

const fetchData = async () => {
  isLoading.value = true
  error.value = null
  try {
    const [fetchedReports, members] = await Promise.all([fetchReports(), fetchMembers()])
    reports.value = processReports(fetchedReports, members)
  } catch (err) {
    console.error('Error in fetchData:', err)
    error.value = `データの取得に失敗しました: ${err.message}`
  } finally {
    isLoading.value = false
  }
}

onMounted(fetchData)

const handleFeedback = async (memberUuid) => {
  const report = reports.value.find(r => r.memberUuid === memberUuid)
  if (report && newFeedback.value.trim() !== '') {
    try {
      const feedback = {
        content: newFeedback.value.trim(),
        createdAt: new Date().toISOString()
      }
      
      await submitFeedback(memberUuid, props.weekString, feedback)
      
      // ローカルの状態を更新
      const updatedReport = {
        ...report,
        feedbacks: [...(report.feedbacks || []), feedback],
        status: 'feedback'
      }
      reports.value = reports.value.map(r =>
        r.memberUuid === memberUuid 
          ? updatedReport
          : r
      )
      // 入力欄をクリア
      newFeedback.value = ''
      showNotification('フィードバックを送信しました')
    } catch (error) {
      console.error('Failed to submit feedback:', error)
      showNotification('フィードバックの送信に失敗しました', 'error')
    }
  }
}

const handleApprove = async (memberUuid) => {
  const now = new Date()
  const report = reports.value.find(r => r.memberUuid === memberUuid)
  if (report) {
    try {
      const updatedReport = {
        ...report,
        status: 'approved',
        approvedAt: now.toISOString()
      }
      await updateReport(updatedReport)
      showNotification('報告を確認済みとしました')
      
      // ローカルの状態を更新
      reports.value = reports.value.map(r =>
        r.memberUuid === memberUuid 
          ? { ...r, status: 'approved', approvedAt: now.toLocaleString() }
          : r
      )
    } catch (error) {
      console.error('Failed to approve report:', error)
      showNotification('報告の承認に失敗しました', 'error')
    }
  }
}
</script>

<style scoped>
.review-form-container {
  padding: 16px 0 24px;
}

.none-card {
  background-color: whitesmoke;
}

.approved-card {
  background-color: white;
}

.tasks {
  background-color: transparent;
}

.v-list-item__title {
  font-size: 0.875rem !important;
}

.v-list-item__subtitle {
  font-size: 0.75rem !important;
}

.borderless-textarea :deep() .v-field__outline {
  display: none;
}

.borderless-textarea :deep() .v-field__overlay {
  background-color: transparent;
}
</style>