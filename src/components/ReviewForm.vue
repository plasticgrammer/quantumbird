<template>
  <v-container class="review-form-container">
    <v-row>
      <v-col
        v-for="report in reports"
        :key="report.id"
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
                      {{ project.tasks }}
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
                  v-model="report.feedback"
                  label="フィードバックを入力..."
                  outlined
                  dense
                  clear-icon="mdi-close-circle"
                  clearable 
                  rows="2"
                  class="small-text-area"
                />

                <v-alert
                  v-if="report.status === 'feedback'"
                  type="warning"
                  outlined
                  dense
                  class="mb-0"
                >
                  <div class="font-weight-bold">
                    フィードバック:
                  </div>
                  <p>{{ report.feedback }}</p>
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
              color="success"
              variant="elevated" 
              outlined
              x-small
              @click="handleApprove(report.id)"
            >
              <v-icon
                left
                x-small
                class="mr-1"
              >
                mdi-check-bold
              </v-icon>
              確認
            </v-btn>
            <v-btn
              color="warning"
              variant="elevated" 
              :disabled="!report.feedback.trim()"
              class="ml-2"
              outlined
              x-small
              @click="submitFeedback(report.id)"
            >
              <v-icon
                left
                x-small
                class="mr-1"
              >
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
import { listReports } from '../services/reportService'
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

const handleApprove = (id) => {
  const now = new Date()
  reports.value = reports.value.map(report =>
    report.id === id
      ? { ...report, status: 'approved', feedback: '', approvedAt: now.toLocaleString() }
      : report
  )
}

const submitFeedback = (id) => {
  const report = reports.value.find(r => r.id === id)
  if (report && report.feedback.trim() !== '') {
    reports.value = reports.value.map(r =>
      r.id === id ? { ...r, status: 'feedback' } : r
    )
  }
}

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
    return fetchedReports.map(report => ({
      id: report.memberUuid,
      projects: report.projects.map(project => ({
        name: project.name,
        tasks: project.workItems.map(item => item.content).join(', ')
      })),
      overtime: report.overtimeHours,
      achievements: report.achievements,
      issues: report.issues,
      improvements: report.improvements,
      status: report.status || 'pending',
      feedback: report.feedback || '',
      approvedAt: report.approvedAt || null
    }))
  } catch (err) {
    console.error('Failed to fetch reports:', err)
    throw err
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
      const report = fetchedReports.find(r => r.id === member.memberUuid) || {}
      return {
        id: member.memberUuid,
        memberId: member.id,
        name: member.name,
        projects: report.projects || [],
        overtime: report.overtime || 0,
        achievements: report.achievements || '',
        issues: report.issues || '',
        improvements: report.improvements || '',
        status: report.status || 'none',
        feedback: report.feedback || '',
        approvedAt: report.approvedAt || null
      }
    }).sort((a, b) => a.memberId.localeCompare(b.memberId, undefined, { numeric: true, sensitivity: 'base' }))
  } catch (err) {
    error.value = '報告書またはメンバー情報の取得に失敗しました。'
  } finally {
    isLoading.value = false
  }
}

onMounted(fetchData)
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
</style>