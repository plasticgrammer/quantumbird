<template>
  <v-container class="review-form-container">
    <v-row class="d-print-none mt-2">
      <v-col cols="12" class="py-0">
        <v-card
          class="px-4"
          rounded="lg"
          variant="text"
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
          hover
          outlined
          class="mt-2"
        >
          <v-card-title class="d-flex justify-space-between align-center py-2">
            <span class="text-h6 font-weight-bold">
              <v-icon
                size="x-large"
                class="mr-1"
              >mdi-account-box-outline</v-icon>
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
                <div class="text-subtitle-2 font-weight-medium mb-1">
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

                <div class="text-subtitle-2 font-weight-medium mb-1">
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

            <v-row class="mt-2">
              <v-col cols="12">
                <v-textarea
                  v-if="report.status !== 'approved'"
                  v-model="newFeedback"
                  label="新しいフィードバックを入力..."
                  outlined
                  dense
                  class="d-print-none"
                  clear-icon="mdi-close-circle"
                  clearable 
                  rows="2"
                />

                <v-alert
                  v-for="(feedback, index) in report.feedbacks" :key="index" 
                  icon="mdi-reply"
                  density="compact"
                  border="start"
                  border-color="warning"
                  elevation="2"
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
                  <v-textarea
                    v-if="!!feedback.replyComment"
                    v-model="feedback.replyComment"
                    label="返信コメント"
                    readonly
                    rows="1"
                    auto-grow
                    outlined
                    dense
                    hide-details
                    class="my-2"
                  >
                    <template #prepend-inner>
                      <v-icon
                        size="large"
                        class="mr-1"
                        color="black"
                      >
                        mdi-message
                      </v-icon>
                    </template>
                  </v-textarea>
                </v-alert>
              </v-col>
            </v-row>
          </v-card-text>

          <v-card-actions
            v-if="report.status !== 'approved' && report.status !== 'none'"
            class="d-print-none py-1"
          >
            <v-spacer />
            <v-btn
              color="primary"
              variant="elevated" 
              outlined
              x-small
              @click="submitApprove(report.memberUuid)"
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
import { ref, computed, watch, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useReport } from '../composables/useReport'
import { listReports, updateReport } from '../services/reportService'
import { listMembers } from '../services/memberService'

const store = useStore()
const { statusOptions, getStatusText, getStatusColor } = useReport()
const organizationId = store.getters['user/organizationId']

const props = defineProps({
  weekString: {
    type: String,
    required: true
  }
})

const reports = ref([])
const isLoading = ref(true)
const error = ref(null)
const newFeedback = ref('')

const selectedStatus = ref('all')

watch(selectedStatus, (newValue) => {
  if (newValue === undefined) {
    selectedStatus.value = 'all'
  }
})

const statusCounts = computed(() => {
  const counts = {
    all: reports.value.length,
    none: 0,
    pending: 0,
    feedback: 0,
    approved: 0
  }

  reports.value.forEach(report => {
    counts[report.status]++
  })

  return counts
})

const filteredReports = computed(() => {
  if (selectedStatus.value === 'all') {
    return reports.value
  }
  return reports.value.filter(report => selectedStatus.value === report.status)
})

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
    }
  }
}

const submitApprove = async (memberUuid) => {
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
    }
  }
}
</script>

<style scoped>
.review-form-container {
  padding: 16px 0 0;
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

.custom-feedback-alert :deep() .v-icon {
  color: orange;
}
</style>