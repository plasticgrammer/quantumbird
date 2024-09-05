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
          class="default-card cursor-default mt-2"
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
              elevation="0"
              variant="flat"
              color="blue-lighten-5"
              title="評価"
            >
              <template #prepend>
                <v-icon icon="mdi-poll"></v-icon>
              </template>
              <v-card-text class="px-6">
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

            <v-row
              v-if="report.status !== 'approved' || report.feedbacks.length" 
              class="mt-2"
            >
              <v-col cols="12">
                <v-alert
                  density="compact"
                  class="feedback-box px-2"
                  border="start"
                  border-color="orange"
                  outlined
                  dense
                >
                  <v-alert-title class="pl-3 pb-2 text-body-1">
                    <v-icon class="mr-2" color="orange" size="large">
                      mdi-comment-text-outline
                    </v-icon>
                    フィードバック
                  </v-alert-title>
                  <div
                    v-for="(feedback, index) in report.feedbacks"
                    :key="index"
                    class="pa-0"
                  >
                    <v-textarea
                      v-model="feedback.content"
                      :label="`${ formatDateTimeJp(new Date(feedback.createdAt)) }`"
                      readonly
                      rows="1"
                      auto-grow
                      hide-details
                      density="comfortable"
                      class="borderless-textarea"
                    >
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
                      class="ml-4 mt-n2 borderless-textarea"
                    >
                      <template #prepend-inner>
                        <v-icon class="mr-1" color="grey-darken-3" size="large">
                          mdi-comment-account-outline
                        </v-icon>
                      </template>
                    </v-textarea>
                  </div>

                  <div 
                    v-if="report.status !== 'approved' && !readonly"
                    class="pl-4 pr-3 py-1 d-print-none"
                  >
                    <v-textarea
                      v-model="newFeedbacks[report.memberUuid]"
                      label="新しいフィードバックを入力..."
                      outlined
                      dense
                      clear-icon="mdi-close-circle"
                      clearable 
                      hide-details="auto"
                      rows="2"
                    >
                    </v-textarea>
                    <v-btn
                      color="orange"
                      variant="elevated" 
                      :disabled="!newFeedbacks[report.memberUuid]?.trim()"
                      class="mt-3"
                      outlined
                      @click="handleFeedback(report.memberUuid)"
                    >
                      <v-icon class="mr-1">
                        mdi-reply
                      </v-icon>
                      フィードバック送信
                    </v-btn>
                  </div>
                </v-alert>
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
              class="mr-2"
              outlined
              @click="handleApprove(report.memberUuid)"
            >
              <v-icon left x-small class="mr-1">
                mdi-check-bold
              </v-icon>
              確認済み
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>

      <v-col 
        v-if="statusCounts['none'] > 0 && !readonly"
        cols="12"
      >
        <v-btn
          color="secondary"
          variant="elevated" 
          outlined
          @click="handleResend()"
        >
          <v-icon class="mr-1">
            mdi-send
          </v-icon>
          報告要求を再送する（報告なし{{ statusCounts['none'] }}名）
        </v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, computed, watchEffect, onMounted, inject } from 'vue'
import { useCalendar } from '../composables/useCalendar'
import { useReport } from '../composables/useReport'
import { listReports, listMembers } from '../services/publicService'
import { updateReport, submitFeedback } from '../services/reportService'
import { generateToken } from '../services/secureParameterService'
import { sendRequest } from '../services/sendRequestService'
import RatingItem from '../components/RatingItem.vue'

const { formatDateTimeJp } = useCalendar()
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
const newFeedbacks = ref({})

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
    
    // ルートURLを取得する関数
    const getRootUrl = () => {
      const { protocol, host, pathname } = window.location
      const pathSegments = pathname.split('/').filter(segment => segment !== '')
      
      // GitHub Pages の場合、最初のセグメントがリポジトリ名
      const repoName = pathSegments[0]
      
      // 開発環境の場合は window.location.origin をそのまま使用
      // 本番環境（GitHub Pages）の場合は、リポジトリ名を含めたパスを使用
      return process.env.NODE_ENV === 'production' 
        ? `${protocol}//${host}/${repoName}`
        : `${protocol}//${host}`
    }

    const rootUrl = getRootUrl()
    const shareUrl = `${rootUrl}/view/${result.token}`
    
    await navigator.clipboard.writeText(shareUrl)
    showNotification('共有リンクをコピーしました')
  } catch (err) {
    console.error('Failed to copy share URL:', err)
    showNotification('共有リンクのコピーに失敗しました', 'error')
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

const handleFeedback = async (memberUuid) => {
  const report = reports.value.find(r => r.memberUuid === memberUuid)
  const newFeedback = newFeedbacks.value[memberUuid]
  if (report && newFeedback && newFeedback.trim() !== '') {
    try {
      const feedback = {
        content: newFeedback.trim(),
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
      newFeedbacks.value[memberUuid] = ''
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

const handleResend = async () => {
  try {
    await sendRequest(props.organizationId, props.weekString)
    showNotification('報告要求を再送しました')
  } catch (error) {
    console.error('Failed to approve report:', error)
    showNotification('報告要求の再送に失敗しました', 'error')
  }
}

const fetchData = async () => {
  isLoading.value = true
  error.value = null
  try {
    const [fetchedReports, members] = await Promise.all([fetchReports(), fetchMembers()])
    reports.value = processReports(fetchedReports, members)
    // 各メンバーのフィードバック入力欄を初期化
    reports.value.forEach(report => {
      newFeedbacks.value[report.memberUuid] = ''
    })
  } catch (err) {
    console.error('Error in fetchData:', err)
    error.value = `データの取得に失敗しました: ${err.message}`
  } finally {
    isLoading.value = false
  }
}
onMounted(fetchData)
</script>

<style scoped>
.review-form-container {
  padding: 16px 0 24px;
}

.default-card {
  background-color: #fafafa;
}

.none-card {
  color: #757575;
}

.approved-card {
  background-color: #fafafa;
}

.tasks {
  background-color: transparent;
}

.feedback-box {
  border: 1px solid rgb(0 0 0 / 0.2) !important;
  background-color: transparent;
}

.v-list-item__title {
  font-size: 0.875rem !important;
}

.v-list-item__subtitle {
  font-size: 0.75rem !important;
}
</style>