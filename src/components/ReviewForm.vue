<template>
  <v-container class="review-form-container">
    <v-row>
      <v-col
        v-for="report in reports"
        :key="report.memberUuid"
        cols="12"
      >
        <v-card
          :class="{ 'approved-card': report.status === 'approved', 'none-card': report.status === 'none' }"
          elevation="4"
          hover
          outlined
          class="mt-2"
        >
          <v-card-title class="d-flex justify-space-between align-center py-2">
            <span class="text-h6 font-weight-bold">
              <v-icon
                size="x-large"
                class="mr-1"
                color="black"
              >mdi-account-box-outline</v-icon>
              {{ report.name }}
            </span>
            <v-chip
              :color="getStatusColor(report.status)"
              outlined
              x-small
              class="ml-2"
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
                md="6"
              >
                <div class="text-subtitle-2 font-weight-medium mb-1">
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
                    <v-list-item-title class="text-body-2">
                      <v-icon small>
                        mdi-clipboard-check-outline
                      </v-icon>
                      {{ project.name }}
                    </v-list-item-title>
                    <v-list-item-subtitle class="ml-2 my-2">
                      {{ toTasks(project) }}
                    </v-list-item-subtitle>
                  </v-list-item>
                </v-list>
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
              </v-col>
              <v-col
                cols="12"
                md="6"
              >
                <div class="text-subtitle-2 font-weight-medium mb-1">
                  現状・問題点
                </div>
                <v-textarea
                  v-model="report.issues"
                  outlined
                  readonly
                  dense
                  auto-grow
                  rows="2"
                  hide-details
                  class="small-text-area mb-2"
                />

                <div class="text-subtitle-2 font-weight-medium mb-1">
                  成果
                </div>
                <v-textarea
                  v-model="report.achievements"
                  outlined
                  readonly
                  dense
                  auto-grow
                  rows="1"
                  hide-details
                  class="small-text-area mb-2"
                />

                <div class="text-subtitle-2 font-weight-medium mb-1">
                  改善点
                </div>
                <v-textarea
                  v-model="report.improvements"
                  outlined
                  readonly
                  dense
                  auto-grow
                  rows="1"
                  hide-details
                  class="small-text-area"
                />
              </v-col>
            </v-row>

            <v-row class="mt-2">
              <v-col cols="12">
                <v-textarea
                  v-if="report.status !== 'approved'"
                  v-model="newFeedback"
                  label="新しいフィードバックを入力..."
                  outlined
                  dense
                  clear-icon="mdi-close-circle"
                  clearable 
                  rows="2"
                  class="small-text-area"
                />

                <v-alert
                  v-for="(feedback, index) in report.feedbacks" :key="index" 
                  type="warning"
                  icon="mdi-message"
                  border="start"
                  border-color="warning"
                  density="compact"
                  outlined
                  dense
                  class="mb-2 custom-feedback-alert"
                >
                  <div class="font-weight-bold">
                    フィードバック（{{ new Date(feedback.createdAt).toLocaleString() }}）:
                  </div>
                  <div class="mt-2">
                    <p>{{ feedback.content }}</p>
                  </div>
                </v-alert>
              </v-col>
            </v-row>
          </v-card-text>

          <v-card-actions
            v-if="report.status !== 'approved' && report.status !== 'none'"
            class="py-1"
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
              確認
            </v-btn>
            <v-btn
              color="warning"
              variant="elevated" 
              :disabled="!newFeedback.trim()"
              class="ml-2"
              outlined
              x-small
              @click="submitFeedback(report.memberUuid)"
            >
              <v-icon left x-small class="mr-1">
                mdi-message
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
import { ref, onMounted } from 'vue'
import { listReports, updateReport } from '../services/reportService'
import { listMembers } from '../services/memberService'
import { useStore } from 'vuex'

const store = useStore()
const organizationId = store.getters['user/organizationId']

const props = defineProps({
  weekString: {
    type: String,
    required: true
  }
})

const reports = ref([])
const isLoading = ref(false)
const error = ref(null)
const newFeedback = ref('')

const getStatusText = (status) => {
  switch (status) {
  case 'none':
    return '報告なし'
  case 'pending':
    return '保留中'
  case 'approved':
    return '確認済み'
  case 'feedback':
    return 'フィードバック済み'
  default:
    return ''
  }
}

const getStatusColor = (status) => {
  switch (status) {
  case 'none':
    return 'error'
  case 'pending':
    return 'grey'
  case 'approved':
    return 'success'
  case 'feedback':
    return 'warning'
  default:
    return ''
  }
}

const fetchReports = async () => {
  try {
    const fetchedReports = await listReports(organizationId, props.weekString)
    
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

const toTasks = (project) => {
  return Array.isArray(project.workItems) 
    ? project.workItems.map(item => item.content).join(', ')
    : ''
}

const fetchMembers = async () => {
  try {
    return await listMembers(organizationId)
  } catch (err) {
    console.error('Failed to fetch members:', err)
    throw err
  }
}

const fetchData = async () => {
  isLoading.value = true
  error.value = null
  try {
    const [fetchedReports, members] = await Promise.all([fetchReports(), fetchMembers()])
    
    reports.value = members.map(member => {
      const report = fetchedReports.find(r => r.memberUuid === member.memberUuid) || {}
      const combinedReport = {
        memberUuid: member.memberUuid,
        weekString: props.weekString,
        organizationId: organizationId,
        memberId: member.id,
        name: member.name,
        projects: report.projects || [],
        overtime: report.overtime || 0,
        achievements: report.achievements || '',
        issues: report.issues || '',
        improvements: report.improvements || '',
        status: report.status || 'none',
        feedbacks: report.feedbacks || [],
        approvedAt: report.approvedAt || null
      }
      return combinedReport
    }).sort((a, b) => a.memberId.localeCompare(b.memberId, undefined, { numeric: true, sensitivity: 'base' }))
  } catch (err) {
    console.error('Error in fetchData:', err)
    error.value = `データの取得に失敗しました: ${err.message}`
  } finally {
    isLoading.value = false
  }
}

onMounted(fetchData)

const submitFeedback = async (memberUuid) => {
  const report = reports.value.find(r => r.memberUuid === memberUuid)
  if (report && newFeedback.value.trim() !== '') {
    try {
      const updatedReport = {
        ...report,
        feedbacks: [
          ...(report.feedbacks || []),
          {
            content: newFeedback.value.trim(),
            createdAt: new Date().toISOString()
          }
        ],
        status: 'feedback'
      }
      await updateReport(updatedReport)
      
      // ローカルの状態を更新
      reports.value = reports.value.map(r =>
        r.memberUuid === memberUuid 
          ? { ...updatedReport }
          : r
      )
      // 入力欄をクリア
      newFeedback.value = ''
    } catch (error) {
      console.error('Failed to submit feedback:', error)
      console.error('Report state:', JSON.stringify(report, null, 2))
      // エラーハンドリング（例：エラーメッセージを表示）
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
      
      // ローカルの状態を更新
      reports.value = reports.value.map(r =>
        r.memberUuid === memberUuid 
          ? { ...r, status: 'approved', approvedAt: now.toLocaleString() }
          : r
      )
    } catch (error) {
      console.error('Failed to approve report:', error)
      // エラーハンドリング（例：エラーメッセージを表示）
    }
  }
}
</script>

<style scoped>
.review-form-container {
  max-width: 800px;
}

.none-card {
  background-color: whitesmoke;
}

.approved-card {
  background-color: azure;
}

.tasks {
  background-color: transparent;
}

.small-text-area :deep() textarea {
  font-size: 0.875rem;
  line-height: 1.25;
}

.v-list-item__title {
  font-size: 0.875rem !important;
}

.v-list-item__subtitle {
  font-size: 0.75rem !important;
}

.custom-feedback-alert {
  color: dimgray !important;
  background-color: whitesmoke !important;
}
</style>