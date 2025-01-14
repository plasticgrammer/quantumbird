<template>
  <v-container class="review-form-container">
    <ScrollNavigation 
      v-if="filteredReports.length > 0"
      class="d-none d-md-flex"
      :report-refs="reportRefs" 
    />

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
      <v-col cols="12" md="2" class="text-end d-none d-md-block">
        <v-btn
          color="secondary"
          size="small"
          @click="copyShareUrl"
        >
          共有する
          <v-icon class="ml-1">
            mdi-share-variant
          </v-icon>
        </v-btn>
      </v-col>
    </v-row>
    <v-row v-if="isLoading && !readonly">
      <v-col>
        <v-skeleton-loader
          type="chip@3"
          class="bg-transparent"
          :loading="true"
        ></v-skeleton-loader>
      </v-col>
    </v-row>

    <v-row v-if="isLoading">
      <v-col v-for="i in 3" :key="i" cols="12">
        <v-skeleton-loader
          type="avatar, text, ossein, paragraph, text, actions"
          class="rounded-lg"
          :loading="true"
          elevation="4"
        ></v-skeleton-loader>
      </v-col>
    </v-row>
    <v-row v-else>
      <v-col cols="12">
        <v-card
          v-for="(report, index) in filteredReports"
          :key="report.memberUuid"
          :ref="el => { if (el) reportRefs[index] = el }"
          :class="{ 'approved-card': report.status === 'approved', 'none-card': report.status === 'none' }"
          class="default-card rounded-lg cursor-default mt-2 pb-1"
          hover
          outlined
        > 
          <v-card-title class="d-flex justify-space-between align-center py-2">
            <div class="d-flex align-center">
              <v-icon size="x-large" class="mr-2">
                mdi-account-box-outline
              </v-icon>
              <span class="text-h6 font-weight-bold">{{ report.name }}</span>
            </div>
            <div class="d-flex align-center">
              <v-tooltip
                :disabled="report.status !== 'approved'"
                location="bottom"
                :close-delay="1500"
              >
                <template #activator="{ props: tooltipProps }">
                  <v-chip
                    v-bind="tooltipProps"
                    :color="getStatusColor(report.status)"
                    label
                    x-small
                    class="status-chip ml-2"
                  >
                    <v-icon
                      v-if="report.status === 'approved'"
                      class="mr-1"
                    >
                      mdi-check-circle-outline
                    </v-icon>
                    {{ getStatusText(report.status) }}
                  </v-chip>
                </template>
                <span>確認日時：{{ formatDateTimeJp(new Date(report.approvedAt)) }}</span>
              </v-tooltip>
              <v-btn
                v-if="!readonly"
                variant="tonal"
                icon
                color="secondary"
                class="ml-2"
                :to="{ name: 'MemberReports', params: { memberUuid: report.memberUuid }}"
              >
                <v-icon size="26" class="opacity-60">mdi-calendar-text</v-icon>
                <v-tooltip activator="parent" location="top">
                  履歴を表示
                </v-tooltip>
              </v-btn>
            </div>
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
                  class="bg-transparent pa-0 mb-3"
                >
                  <v-list-item
                    v-for="(project, projectIndex) in report.projects"
                    :key="projectIndex"
                    class="px-2 py-2"
                  >
                    <v-list-item-title>
                      <v-icon small>
                        mdi-folder-outline
                      </v-icon>
                      {{ project.name }}
                    </v-list-item-title>
                    <v-list-item-subtitle class="d-block ml-2 my-2">
                      <ul class="work-items-list text-black">
                        <li v-for="(item, itemIndex) in project.workItems" :key="itemIndex">
                          {{ item.content }}
                        </li>
                      </ul>
                    </v-list-item-subtitle>
                  </v-list-item>
                </v-list>
                <div v-if="report.overtimeHours >= 0" class="mt-auto">
                  <OvertimeDisplay :overtime-hours="report.overtimeHours" />
                </div>
              </v-col>
              <v-col
                cols="12"
                md="7"
              >
                <div class="text-subtitle-1 font-weight-medium mb-1">
                  振り返り（成果と課題）
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
                  次の目標、改善施策
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
              color="#e6f3ff"
            >
              <v-card-title>
                <div class="d-flex align-center">
                  <v-icon icon="mdi-equalizer" color="blue-grey-darken-3" class="mr-2"></v-icon>
                  評価
                </div>
              </v-card-title>
              <v-card-text>
                <rating-item
                  v-for="item in preparedRatingItems"
                  :key="item.key"
                  :model-value="item.getValue(report)"
                  :label="item.label"
                  :item-labels="item.labels"
                  :negative="item.negative"
                  :readonly="true"
                  :comparison="item.getComparison(report)"
                />
                <v-textarea
                  v-if="report.stressHelp"
                  v-model="report.stressHelp"
                  label="ストレス度：必要な支援や状況の詳細"
                  readonly
                  rows="1"
                  auto-grow
                  hide-details
                  variant="outlined"
                  density="comfortable"
                  class="mt-8 mx-2"
                ></v-textarea>
              </v-card-text>
            </v-card>
            
            <v-row
              v-if="(!readonly) || report.feedbacks.length" 
              class="mt-2"
            >
              <v-col cols="12">
                <v-expansion-panels 
                  v-model="expandedPanels[report.memberUuid]" 
                  elevation="2"
                  eager
                  @update:model-value="value => expandedPanels[report.memberUuid] = value"
                >
                  <v-expansion-panel>
                    <v-expansion-panel-title class="bg-plain">
                      <v-alert-title class="text-body-1 d-flex align-center">
                        <v-icon class="mr-2" color="orange">
                          mdi-comment-text-outline
                        </v-icon>
                        フィードバック
                        <v-badge
                          v-if="report.feedbacks.length"
                          color="orange-darken-1"
                          class="ml-1"
                          :content="report.feedbacks.length"
                          inline
                        ></v-badge>
                      </v-alert-title>
                    </v-expansion-panel-title>
                    <v-expansion-panel-text>
                      <div
                        v-for="(feedback, feedbackIndex) in report.feedbacks"
                        :key="feedbackIndex"
                        class="pa-0"
                      >
                        <v-textarea
                          v-model="feedback.content"
                          :label="`${formatDateTimeJp(new Date(feedback.createdAt))}`"
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
                        v-if="!readonly"
                        class="mt-2 px-1"
                      >
                        <v-textarea
                          v-model="newFeedbacks[report.memberUuid]"
                          placeholder="新しいフィードバックを入力..."
                          outlined
                          dense
                          clear-icon="mdi-close-circle"
                          clearable 
                          hide-details="auto"
                          rows="2"
                          auto-grow
                        >
                        </v-textarea>
                        <v-btn
                          color="warning"
                          variant="elevated" 
                          :disabled="!newFeedbacks[report.memberUuid]?.trim()"
                          class="mt-3 mb-1"
                          @click="handleFeedback(report.memberUuid)"
                        >
                          <v-icon class="mr-1">
                            mdi-reply
                          </v-icon>
                          フィードバック送信
                        </v-btn>
                      </div>
                    </v-expansion-panel-text>
                  </v-expansion-panel>
                </v-expansion-panels>
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
          @click="handleResend"
        >
          報告要求を送信する
          <v-icon class="ml-1">
            mdi-send
          </v-icon>
        </v-btn>
      </v-col>
    </v-row>

    <ReviewCompleteDialog
      v-model="showCompletionDialog"
      :report-count="reports.length"
      @share="copyShareUrl"
    />
  </v-container>
</template>

<script setup>
import { computed, defineAsyncComponent, inject, nextTick, onMounted, ref, watch, watchEffect } from 'vue'
import { listReports, listMembers } from '@/services/publicService'
import { rootUrl } from '@/config/environment'
import { generateToken } from '@/services/secureParameterService'
import { sendRequest } from '@/services/sendRequestService'
import { submitFeedback, updateReport } from '@/services/reportService'
import { useCalendar } from '@/composables/useCalendar'
import { useReport } from '@/composables/useReport'
import OvertimeDisplay from './OvertimeDisplay.vue'
import RatingItem from './RatingItem.vue'
import ReviewCompleteDialog from './ReviewCompleteDialog.vue'
const ScrollNavigation = defineAsyncComponent(() => import('./ScrollNavigation.vue'))

const { formatDateTimeJp, formatDateJp, getPreviousWeekString } = useCalendar()
const { statusOptions, getStatusText, getStatusColor, ratingItems } = useReport()
const showNotification = inject('showNotification')
const showError = inject('showError')
const showConfirmDialog = inject('showConfirmDialog')

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
const selectedStatus = ref('all')
const lastWeekRatings = ref({})
const expandedPanels = ref({})
const newFeedbacks = ref({})

const unconfirmedCount = computed(() => {
  return statusCounts.value['none'] || 0
})

const shouldExpandPanel = computed(() => {
  return reports.value.reduce((acc, report) => {
    const feedbacks = report.feedbacks ?? []
    acc[report.memberUuid] = feedbacks.length > 0 ? [0] : []
    return acc
  }, {})
})

const updateExpandedPanels = () => {
  expandedPanels.value = { ...shouldExpandPanel.value }
}

watchEffect(() => {
  if (selectedStatus.value === undefined) {
    selectedStatus.value = 'all'
  }
})

watchEffect(() => {
  if (reports.value.length > 0) {
    updateExpandedPanels()
  }
})

// メモ化されたステータスカウント
const statusCounts = computed(() => {
  return reports.value.reduce((counts, report) => {
    counts[report.status] = (counts[report.status] || 0) + 1
    return counts
  }, { all: reports.value.length })
})

// 全員の報告が確認済みかどうかの判定
const isAllCompleted = computed(() => {
  return reports.value.length > 0 && reports.value.every(report => report.status === 'approved')
})

// メモ化されたフィルタリング
const filteredReports = computed(() => 
  selectedStatus.value === 'all' 
    ? reports.value 
    : reports.value.filter(report => report.status === selectedStatus.value)
)

const copyShareUrl = async () => {
  try {
    const params = { organizationId: props.organizationId, weekString: props.weekString }
    const result = await generateToken(params)
    
    const shareUrl = `${rootUrl}/view/${result.token}#_=`
    
    // 14日後の日付を計算
    const expiryDate = new Date()
    expiryDate.setDate(expiryDate.getDate() + 14)
    const comment = `有効期限：${formatDateJp(expiryDate)}`
    
    const shareText = `${shareUrl}\n${comment}`
    
    await navigator.clipboard.writeText(shareText)
    showNotification('共有リンクをコピーしました')
  } catch (err) {
    showError('共有リンクのコピーに失敗しました', err)
  }
}

const preparedRatingItems = computed(() => {
  // 達成度の表示を反転させる
  return ratingItems.map(item => ({
    ...item,
    labels: item.key === 'achievement' ? item.itemLabels.slice().reverse() : item.itemLabels,
    negative: item.key === 'achievement' ? !item.negative : item.negative,
    getValue: (report) => {
      const value = report.rating[item.key]
      return item.key === 'achievement' ? item.itemLabels.length - value + 1 : value
    },
    getComparison: (report) => {
      if (lastWeekRatings.value[report.memberUuid]) {
        const value = lastWeekRatings.value[report.memberUuid][item.key]
        return item.key === 'achievement' ? item.itemLabels.length - value + 1 : value
      }
      return null
    }
  }))
})

const fetchReports = async (weekString) => {
  try {
    const fetchedReports = await listReports(props.organizationId, weekString)
    if (!fetchedReports) {
      return []
    }

    return fetchedReports.map(report => {
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

const sortReports = (reports) => {
  const statusOrder = { none: 0, pending: 1, feedback: 2, approved: 3 }
  return [...reports].sort((a, b) => {
    // ステータスでの比較
    const statusDiff = statusOrder[a.status] - statusOrder[b.status]
    if (statusDiff !== 0) return statusDiff
    
    // memberIdでの比較（第2ソートキー）
    return a.memberId.localeCompare(b.memberId)
  })
}

const processReports = (fetchedReports, members) => {
  const reportMap = new Map(fetchedReports.map(r => [r.memberUuid, r]))
  
  const processedReports = members.map(member => {
    const report = reportMap.get(member.memberUuid) || {
      memberUuid: member.memberUuid,
      status: 'none',
      projects: [],
    }
    return {
      ...report,
      memberId: member.id,
      name: member.name,
      projects: report.projects || [],
      status: report.status || 'none',
    }
  })

  return sortReports(processedReports)
}

const handleFeedback = async (memberUuid) => {
  const confirmed = await showConfirmDialog(
    '確認',
    'フィードバックを送信します。よろしいですか？'
  )
  if (!confirmed) {
    return
  }

  const report = reports.value.find(r => r.memberUuid === memberUuid)
  const newFeedback = newFeedbacks.value[memberUuid]
  if (report && newFeedback && newFeedback.trim() !== '') {
    try {
      const feedback = {
        content: newFeedback.trim(),
        createdAt: new Date().toISOString()
      }
      
      await submitFeedback(memberUuid, props.weekString, feedback)
      showNotification('フィードバックを送信しました')
      
      // 入力欄をクリア
      newFeedbacks.value[memberUuid] = ''
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
      reports.value = sortReports(reports.value)

    } catch (error) {
      showError('フィードバックの送信に失敗しました', error)
    }
  }
}

const handleApprove = async (memberUuid) => {
  try {
    const confirmMessage = newFeedbacks.value[memberUuid]?.trim() 
      ? 'フィードバックが未送信です。\nフィードバックの入力を破棄して、報告を確認済みとします。よろしいですか？'
      : '報告を確認済みとします。よろしいですか？'

    const confirmed = await showConfirmDialog('確認', confirmMessage)
    if (!confirmed) return

    const report = reports.value.find(r => r.memberUuid === memberUuid)
    if (!report) {
      showError('報告の確認に失敗しました')
      return
    }

    const now = new Date()
    const updateData = {
      status: 'approved',
      approvedAt: now.toISOString()
    }

    await updateReport({
      ...report,
      ...updateData
    })

    // フィードバック入力欄をクリアし、パネルを閉じる
    newFeedbacks.value[memberUuid] = ''
    expandedPanels.value[memberUuid] = []

    // トランザクション的な処理の改善
    const updatedReports = reports.value.map(r => 
      r.memberUuid === memberUuid 
        ? { ...r, ...updateData }
        : r
    )
    
    reports.value = sortReports(updatedReports)
    showNotification('報告を確認済みとしました')
  } catch (error) {
    showError('報告の確認に失敗しました', error)
  }
}

const handleResend = async () => {
  const confirmed = await showConfirmDialog(
    '確認',
    `報告要求を［報告なし${unconfirmedCount.value}名］に送信します。\nよろしいですか？`
  )

  if (confirmed) {
    try {
      await sendRequest(props.organizationId, props.weekString)
      showNotification('報告要求を送信しました')
    } catch (error) {
      showError('報告要求の送信に失敗しました', error)
    }
  }
}

const fetchData = async () => {
  isLoading.value = true
  error.value = null
  
  try {
    const previousWeekString = getPreviousWeekString(props.weekString)
    const [fetchedReports, fetchedPrevReports, members] = await Promise.allSettled([
      fetchReports(props.weekString), 
      fetchReports(previousWeekString),
      listMembers(props.organizationId)
    ])

    // membersの取得が必須なのでエラーチェック
    if (members.status === 'rejected') {
      throw new Error('メンバー情報の取得に失敗しました')
    }
    // 現在週のレポートは必須なのでエラーチェック
    if (fetchedReports.status === 'rejected') {
      throw new Error('現在の週のレポート取得に失敗しました')
    }

    reports.value = processReports(fetchedReports.value, members.value)
    // 前週のデータは失敗を許容（フォールバック処理）
    lastWeekRatings.value = fetchedPrevReports.status === 'fulfilled' 
      ? fetchedPrevReports.value.reduce((acc, report) => {
        if (report?.rating) {
          acc[report.memberUuid] = report.rating
        }
        return acc
      }, {})
      : {}

    // 初期状態の設定
    initializeState()
    
  } catch (err) {
    error.value = `データの取得に失敗しました: ${err.message}`
    showError('データの読み込みに失敗しました', err)
  } finally {
    isLoading.value = false
  }
}

// 状態初期化を別関数に分離
const initializeState = () => {
  // フィードバック入力欄の初期化
  reports.value.forEach(report => {
    newFeedbacks.value[report.memberUuid] = ''
  })
  
  // その他の状態初期化
  nextTick(() => {
    updateExpandedPanels()
    previousCompletionState.value = isAllCompleted.value
    isInitialized.value = true
    initReportRefs()
  })
}

const reportRefs = ref([])

const initReportRefs = () => {
  reportRefs.value = new Array(filteredReports.value.length).fill(null)
}

watchEffect(() => {
  if (filteredReports.value.length > 0) {
    initReportRefs()
  }
})

onMounted(() => {
  fetchData().then(() => {
    initReportRefs()
  })
})

const showCompletionDialog = ref(false)
const isInitialized = ref(false)
const previousCompletionState = ref(false)

// 初期化完了後のみ監視を実行し、確認済み直後のみダイアログを表示
watch(isAllCompleted, (currentlyComplete) => {
  if (isInitialized.value && !props.readonly && currentlyComplete && !previousCompletionState.value) {
    showCompletionDialog.value = true
  }
  previousCompletionState.value = currentlyComplete
})
</script>

<style scoped>
.review-form-container {
  padding: 16px 0 24px;
}

.none-card {
  color: #757575;
}

.default-card,
.approved-card {
  background-color: #f6fbff;
}

.default-card + .default-card {
  margin-top: 24px !important;
}

.v-list-item__title {
  font-size: 0.875rem !important;
}

.v-list-item__subtitle {
  font-size: 0.75rem !important;
}

.v-expansion-panel-title {
  padding: 4px 16px;
}

.v-expansion-panel--active > .v-expansion-panel-title:not(.v-expansion-panel-title--static) {
  min-height: auto !important;
  padding-top: 13px !important;
  padding-bottom: 12px !important;
}

.borderless-textarea :deep(.v-field__outline) {
  display: none;
}

/* 5. レスポンシブ対応の改善 */
@media (max-width: 600px) {
  .review-form-container {
    padding: 8px 0 16px;
  }

  .default-card + .default-card {
    margin-top: 16px !重要;
  }
}

.v-btn--icon.v-btn--density-comfortable {
  width: 36px;
  height: 36px;
  margin-right: 8px;
}

.v-btn--icon.v-btn--density-comfortable .v-icon {
  font-size: 20px;
}
</style>