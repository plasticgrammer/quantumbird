<template>
  <v-container class="report-form-container">
    <v-skeleton-loader
      v-if="formState.isLoading"
      elevation="4"
      type="text, sentences@2, actions, chip, divider, list-item-three-line, list-item@2, button"
    ></v-skeleton-loader>

    <template v-else>
      <template v-if="isReportConfirmed">
        <v-alert type="info" color="blue-grey" border="start" class="mt-2 mb-6">
          この報告は管理者が確認済みです。編集はできません。
        </v-alert>
      </template>
      <template v-else-if="weekString === getCurrentWeekString()">
        <v-alert type="info" color="light-blue" border="start" class="mt-2 mb-6" closable>
          報告対象期間が終了していません。問題なければ報告を行ってください。
        </v-alert>
      </template>

      <template v-if="!!formState.previousWeekReport && !isReportConfirmed">
        <v-card class="rounded-lg mb-4">
          <v-expansion-panels v-model="formState.expandedPanel">
            <v-expansion-panel>
              <v-expansion-panel-title class="bg-grey-lighten-4">
                <span class="text-decoration-underline" style="text-underline-offset: 4px">
                  前週の報告内容
                </span>
                <template #actions>
                  <v-icon icon="mdi-chevron-down"></v-icon>
                </template>
              </v-expansion-panel-title>
              <v-expansion-panel-text class="bg-plain">
                <v-row>
                  <v-col cols="12" md="5" class="pa-2">
                    <v-list class="bg-transparent custom-list">
                      <v-list-item v-for="(project, index) in formState.previousWeekReport.projects" :key="index">
                        <v-list-item-title>
                          <v-icon small>
                            mdi-folder-outline
                          </v-icon>
                          {{ project.name }}
                        </v-list-item-title>
                        <v-list-item-subtitle class="d-block">
                          <ul class="work-items-list">
                            <li v-for="(item, itemIndex) in project.workItems" :key="itemIndex">
                              {{ item.content }}
                            </li>
                          </ul>
                        </v-list-item-subtitle>
                      </v-list-item>
                    </v-list>
                  </v-col>
                  <v-col cols="12" md="7">
                    <v-textarea
                      v-model="formState.previousWeekReport.issues"
                      label="振り返り（成果と課題）"
                      outlined
                      readonly
                      auto-grow
                      rows="2"
                      hide-details
                      class="small-text-area mb-2"
                    />

                    <v-textarea
                      v-model="formState.previousWeekReport.improvements"
                      label="次の目標、改善施策"
                      outlined
                      readonly
                      auto-grow
                      rows="1"
                      hide-details
                      class="small-text-area"
                    />
                  </v-col>
                </v-row>
                <v-row class="justify-end pa-4 pt-1">
                  <v-btn
                    color="secondary"
                    variant="elevated"
                    @click="copyFromPreviousWeek"
                  >
                    <v-icon class="mr-1">
                      mdi-content-copy
                    </v-icon>
                    作業内容をコピー
                  </v-btn>
                </v-row>
              </v-expansion-panel-text>
            </v-expansion-panel>
          </v-expansion-panels>
        </v-card>
      </template>

      <v-form
        ref="reportForm"
        class="bg-plain rounded-lg mt-3 elevation-6 pa-3 pa-md-5"
        :class="{ 'form-disabled': isReportConfirmed }"
        @submit.prevent="handleSubmit"
      >
        <!-- Projects section -->
        <v-card
          v-for="(project, projectIndex) in formState.report.projects"
          :key="projectIndex" 
          elevation="2"
          class="pb-2 mb-4"
        >
          <v-card-text>
            <v-row>
              <v-col cols="9" md="8" class="pa-1 pa-md-4">
                <ProjectSelector
                  v-model="project.name"
                  :project-names="formState.projectNames"
                  :member-uuid="props.memberUuid"
                  :error-messages="formState.errors.projects[projectIndex]?.name"
                  @project-list-changed="updateProjectList"
                />
              </v-col>
              <v-col cols="3" md="4" class="d-flex justify-end">
                <v-btn
                  icon
                  class="project-delete-btn"
                  tabindex="-1"
                  @click="removeProject(projectIndex)"
                >
                  <v-icon>mdi-delete-outline</v-icon>
                </v-btn>
              </v-col>
            </v-row>
            <v-row v-if="project.workItems.length > 0">
              <v-col cols="12" class="pa-1">
                <div
                  v-for="(item, itemIndex) in project.workItems"
                  :key="itemIndex"
                  class="mb-2"
                >
                  <v-text-field
                    :ref="el => setWorkItemRef(el, projectIndex, itemIndex)"
                    v-model="item.content"
                    :label="`作業内容 ${itemIndex + 1}`"
                    class="work-item-input pl-2 pl-md-5"
                    required
                    hide-details="auto"
                    :error-messages="formState.errors.projects[projectIndex]?.workItems[itemIndex]"
                    @keydown="handleKeyDown($event, project, itemIndex)"
                  >
                    <template #append>
                      <v-icon 
                        :color="item.content ? 'grey darken-2' : 'grey lighten-1'"
                        tabindex="-1"
                        @click="removeWorkItem(project, itemIndex)"
                      >
                        mdi-close-circle-outline
                      </v-icon>
                    </template>
                  </v-text-field>
                </div>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
        <v-fab
          class="me-md-5 mt-n5 mt-md-n2"
          location="top end"
          color="secondary"
          extended
          absolute
          offset
          :disabled="isReportConfirmed" 
          @click="addProject"
        >
          <template #prepend>
            <v-icon class="mx-n2">
              mdi-folder-outline
            </v-icon>
          </template>
          <v-icon class="pl-1 mr-n2">
            mdi-plus
          </v-icon>
        </v-fab>
        
        <!-- Overtime section -->
        <v-row class="mt-4 mt-md-2">
          <v-col cols="12" sm="6">
            <v-text-field
              v-model="formattedOvertimeHours"
              label="残業時間（週単位）"
              type="number"
              min="0"
              max="99"
              step="0.5"
              required
              outlined
              dense
              class="overtime-input"
              @input="updateOvertime"
            >
              <template #append>
                <v-btn
                  icon
                  :size="isMobile ? 38 : 48"
                  @click="decreaseOvertime"
                >
                  <v-icon>mdi-minus</v-icon>
                </v-btn>
                <span class="mr-1"></span>
                <v-btn
                  icon
                  :size="isMobile ? 38 : 48"
                  @click="increaseOvertime"
                >
                  <v-icon>mdi-plus</v-icon>
                </v-btn>
              </template>
            </v-text-field>
          </v-col>
        </v-row>

        <!-- Issues and improvements section -->
        <v-textarea
          v-model="formState.report.issues"
          label="振り返り（成果と課題）"
          required
          rows="3"
          auto-grow
          outlined
          counter
          :error-messages="formState.errors.form.issues"
        >
          <template #append-inner>
            <v-tooltip location="top" max-width="340" :close-delay="500">
              <template #activator="{ props: tooltipProps }">
                <v-icon
                  v-if="!isMobile"
                  v-bind="tooltipProps"
                  color="grey"
                  icon="mdi-tooltip-question-outline"
                  class="cursor-pointer"
                ></v-icon>
              </template>
              <div class="custom-tooltip">
                <p><strong>効果的な振り返りのポイント</strong></p>
                <p>
                  ・ 主要な成果と進捗を具体的に記述する<br>
                  ・ 直面した課題と得られた学びを説明する<br>
                  ・ 可能な限り数値や具体例を含める
                </p>
              </div>
            </v-tooltip>
          </template>
        </v-textarea>
        
        <v-textarea
          v-model="formState.report.improvements"
          label="次の目標、改善施策"
          rows="1"
          auto-grow
          outlined
          :error-messages="formState.errors.form.improvements"
        >
          <template #append-inner>
            <v-tooltip location="top" max-width="340" :close-delay="500">
              <template #activator="{ props: tooltipProps }">
                <v-icon
                  v-if="!isMobile"
                  v-bind="tooltipProps"
                  color="grey"
                  icon="mdi-tooltip-question-outline"
                  class="cursor-pointer"
                ></v-icon>
              </template>
              <div class="custom-tooltip">
                <p><strong>効果的な目標設定と改善施策</strong></p>
                <p>
                  ・ 優先度の高い改善点を明確にする<br>
                  ・ 具体的で測定可能な目標と行動計画を立てる
                </p>
              </div>
            </v-tooltip>
          </template>
        </v-textarea>

        <!-- Rating section -->
        <v-card 
          class="mt-2 border-sm"
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
              v-for="item in ratingItems"
              :key="item.key"
              v-model="formState.report.rating[item.key]"
              :label="item.label"
              :item-labels="item.itemLabels"
              :negative="item.negative"
            />
          </v-card-text>
        </v-card>
        <div v-if="formState.errors.form.rating.length" class="v-input--error">
          <div class="v-input__details">
            <div 
              v-for="(ratingError, index) in formState.errors.form.rating"
              :key="index"
              class="v-messages" 
            >
              <div class="v-messages__message pl-4">
                {{ ratingError }}
              </div>
            </div>
          </div>
        </div>

        <v-row 
          v-if="formState.report.feedbacks && formState.report.feedbacks.length"  
          class="mt-2"
        >
          <v-col cols="12">
            <v-expansion-panels 
              v-model="expandedPanels" 
              class="feedback-box"
              :class="{ 'form-disabled': isReportConfirmed }" 
              elevation="2"
              eager
            >
              <v-expansion-panel>
                <v-expansion-panel-title>
                  <div class="d-flex align-center">
                    <v-icon class="mr-2" color="orange">
                      mdi-comment-text-outline
                    </v-icon>
                    フィードバック
                    <v-badge
                      v-if="formState.report.feedbacks.length"
                      color="orange-darken-1"
                      class="ml-2"
                      :content="formState.report.feedbacks.length"
                      inline
                    ></v-badge>
                  </div>
                </v-expansion-panel-title>
                <v-expansion-panel-text>
                  <div
                    v-for="(feedback, index) in sortedFeedbacks"
                    :key="index"
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
                      v-if="!!feedback.replyComment || isLatestFeedback(index)"
                      v-model="feedback.replyComment"
                      label="返信コメント"
                      :readonly="!isLatestFeedback(index)"
                      :clearable="isLatestFeedback(index)"
                      clear-icon="mdi-close-circle"
                      :rows="isLatestFeedback(index) ? 2 : 1"
                      auto-grow
                      hide-details
                      density="comfortable"
                      class="mx-4"
                      :class="{ 'borderless-textarea': !isLatestFeedback(index), 'mt-n2': !isLatestFeedback(index), 'my-2': isLatestFeedback(index) }"
                    >
                      <template #prepend-inner>
                        <v-icon class="mr-1" color="grey-darken-3" size="large">
                          mdi-reply
                        </v-icon>
                      </template>
                    </v-textarea>
                  </div>
                </v-expansion-panel-text>
              </v-expansion-panel>
            </v-expansion-panels>
          </v-col>
        </v-row>

        <v-row 
          v-if="!isReportConfirmed"
          class="mt-2"
        >
          <v-col cols="12" class="d-flex justify-end">
            <v-btn
              v-if="!formState.isNew"
              color="grey"
              variant="outlined"
              @click="handleUndo"
            >
              <v-icon class="mr-1" left>
                mdi-undo
              </v-icon>
              元に戻す
            </v-btn>
            <span class="mx-2"></span>
            <v-btn
              color="primary"
              type="submit"
              :disabled="isSubmitDisabled"
            >
              <v-icon class="mr-1" left>
                mdi-check
              </v-icon>
              報告を{{ formState.isNew ? '提出' : '更新' }}する
            </v-btn>
          </v-col>
        </v-row>
      </v-form>
    </template>
  </v-container>
</template>

<script setup>
import { ref, computed, nextTick, reactive, inject, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getReport, submitReport, updateReport, getMemberProjects } from '../services/publicService'
import { useCalendar } from '../composables/useCalendar'
import { useReport } from '../composables/useReport'
import { useResponsive } from '../composables/useResponsive'
import ProjectSelector from '../components/ProjectSelector.vue'
import RatingItem from '../components/RatingItem.vue'

const route = useRoute()
const { isMobile } = useResponsive()
const showNotification = inject('showNotification')
const showError = inject('showError')
const showConfirmDialog = inject('showConfirmDialog')

const { formatDateTimeJp, getPreviousWeekString, getCurrentWeekString } = useCalendar()
const { initialReport, ratingItems } = useReport()

const props = defineProps({
  organizationId: {
    type: String,
    required: true
  },
  memberUuid: {
    type: String,
    required: true
  },
  weekString: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['report-submitted'])

const formState = reactive({
  report: initialReport(props.organizationId, props.memberUuid, props.weekString),
  isNew: true,
  isLoading: false,
  projectNames: [],
  previousWeekReport: null,
  expandedPanel: null,
  errors: {
    form: { issues: [], rating: [] },
    projects: []
  }
})

const isSubmitDisabled = computed(() => {
  // 報告が確認済みの場合は常に無効
  if (isReportConfirmed.value) return true

  // 最低限の必須項目のみをチェック
  return formState.report.projects.length === 0 || 
         formState.report.issues.trim() === ''
})

const workItemRefs = reactive({})
const expandedPanels = ref([0])

const isReportConfirmed = computed(() => formState.report.status === 'approved')
const sortedFeedbacks = computed(() => [...(formState.report.feedbacks || [])].sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt)))
const formattedOvertimeHours = computed({
  get: () => (formState.report.overtimeHours ?? 0).toFixed(1),
  set: (value) => { formState.report.overtimeHours = parseFloat(value) }
})

const isLatestFeedback = (index) => index === formState.report.feedbacks.length - 1

const updateProjectList = (newProjectList) => {
  formState.projectNames = newProjectList
}

const updateOvertime = (event) => {
  let value = parseFloat(event.target.value)
  if (isNaN(value)) value = 0
  value = Math.max(0, Math.min(99, value))
  formState.report.overtimeHours = parseFloat(value.toFixed(1))
}

const increaseOvertime = () => {
  if (formState.report.overtimeHours < 99) {
    formState.report.overtimeHours = parseFloat((formState.report.overtimeHours + 0.5).toFixed(1))
  }
}

const decreaseOvertime = () => {
  if (formState.report.overtimeHours > 0) {
    formState.report.overtimeHours = parseFloat((formState.report.overtimeHours - 0.5).toFixed(1))
  }
}

const setWorkItemRef = (el, projectIndex, itemIndex) => {
  if (!workItemRefs[projectIndex]) {
    workItemRefs[projectIndex] = {}
  }
  workItemRefs[projectIndex][itemIndex] = el
}

const handleKeyDown = async (event, project, itemIndex) => {
  if (event.key === 'Enter' && !event.isComposing) {
    event.preventDefault()
    const isLastItem = itemIndex === project.workItems.length - 1
    
    if (isLastItem && project.workItems[itemIndex].content.trim() !== '') {
      await addWorkItem(project)
      focusNewWorkItem(project, itemIndex + 1)
    } else {
      focusNextField(project, itemIndex)
    }
  }
}

const addWorkItem = async (project) => {
  project.workItems.push({ content: '' })
  await nextTick()
}

const focusNewWorkItem = (project, newIndex) => {
  const projectIndex = formState.report.projects.indexOf(project)
  nextTick(() => {
    if (workItemRefs[projectIndex] && workItemRefs[projectIndex][newIndex]) {
      workItemRefs[projectIndex][newIndex].focus()
    }
  })
}

const focusNextField = (project, currentIndex) => {
  const projectIndex = formState.report.projects.indexOf(project)
  const nextIndex = currentIndex + 1
  
  nextTick(() => {
    if (workItemRefs[projectIndex] && workItemRefs[projectIndex][nextIndex]) {
      workItemRefs[projectIndex][nextIndex].focus()
    } else {
      const form = document.querySelector('.report-form')
      const inputs = form.querySelectorAll('input, textarea, select')
      const currentInput = workItemRefs[projectIndex][currentIndex]
      const currentInputIndex = Array.from(inputs).indexOf(currentInput)
      
      if (currentInputIndex !== -1 && currentInputIndex < inputs.length - 1) {
        inputs[currentInputIndex + 1].focus()
      }
    }
  })
}

const removeWorkItem = (project, index) => {
  project.workItems.splice(index, 1)
  if (project.workItems.length === 0) {
    addWorkItem(project)
  }
}

const copyFromPreviousWeek = () => {
  if (formState.previousWeekReport) {
    formState.report = {
      ...formState.report,
      projects: formState.previousWeekReport.projects?.map(project => ({
        ...project,
        workItems: project.workItems.map(item => ({ ...item }))
      })) || [],
    }
  }
}

const addProject = () => {
  formState.report.projects.push({ name: '', workItems: [{ content: '' }] })
}

const removeProject = (projectIndex) => {
  if (formState.report.projects.length === 1) {
    formState.report.projects[0].name = ''
    formState.report.projects[0].workItems = [{ content: '' }]
  } else {
    formState.report.projects.splice(projectIndex, 1)
  }
}

const scrollToFeedback = () => {
  const feedbackElement = document.querySelector('.feedback-box')
  if (feedbackElement) {
    feedbackElement.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

const checkAndScrollToFeedback = () => {
  if (route.query.feedback === 'true' && formState.report.feedbacks?.length > 0) {
    nextTick(() => {
      scrollToFeedback()
    })
  }
}

const fetchReport = async () => {
  formState.isLoading = true
  try {
    const previousWeekString = getPreviousWeekString(props.weekString)
    const [fetchedReport, fetchedPrevReport, memberProjects] = await Promise.all([
      getReport(props.memberUuid, props.weekString),
      getReport(props.memberUuid, previousWeekString),
      getMemberProjects(props.memberUuid)
    ])

    formState.isNew = true
    if (fetchedReport) {
      formState.isNew = false
      formState.report = {
        ...fetchedReport,
        issues: fetchedReport.issues || '',
        improvements: fetchedReport.improvements || '',
        rating: fetchedReport.rating || {}
      }
    }
    if (fetchedPrevReport) {
      formState.previousWeekReport = {
        ...fetchedPrevReport,
        issues: fetchedPrevReport.issues || ' ',
        improvements: fetchedPrevReport.improvements || ' '
      }
    }
    formState.projectNames = memberProjects
  } catch (err) {
    showError('報告書またはプロジェクトリストの取得に失敗しました。', err)
  } finally {
    formState.isLoading = false
  }
}

const validateReport = () => {
  let isValid = true
  
  // エラーメッセージをクリア
  formState.errors.form.issues = []
  formState.errors.form.rating = []
  formState.errors.projects = []

  if (formState.report.projects.length === 0) {
    isValid = false
    formState.errors.form.issues.push('少なくとも1つのプロジェクトを追加してください。')
  }

  formState.report.projects.forEach((project, index) => {
    if (!project.name.trim()) {
      isValid = false
      formState.errors.projects[index] = formState.errors.projects[index] || {}
      formState.errors.projects[index].name = ['プロジェクト名を入力してください。']
    }
    const validWorkItems = project.workItems.filter(item => item.content.trim() !== '')
    if (validWorkItems.length === 0) {
      isValid = false
      formState.errors.projects[index] = formState.errors.projects[index] || {}
      formState.errors.projects[index].workItems = ['少なくとも1つの作業内容を追加してください。']
    }
  })

  if (!formState.report.issues.trim()) {
    isValid = false
    formState.errors.form.issues.push('振り返り（成果と課題）は必須入力です。')
  }

  if (!formState.report.rating?.achievement || !formState.report.rating?.disability || !formState.report.rating?.stress) {
    isValid = false
    formState.errors.form.rating.push('評価は必須入力です。')
  }

  return isValid
}

const removeEmptyWorkItems = (projects) => {
  return projects.map(project => ({
    ...project,
    workItems: project.workItems.filter(item => item.content.trim() !== '')
  }))
}

const handleSubmit = async () => {
  if (isReportConfirmed.value) {
    showNotification('確認済みの報告書は編集できません。', 'info')
    return
  }

  const isValid = validateReport()

  if (!isValid) {
    showError('入力に誤りがあります。赤字箇所を確認してください。')
    return
  }

  const cleanedReport = {
    ...formState.report,
    projects: removeEmptyWorkItems(formState.report.projects),
    status: 'pending'
  }

  const confirmed = await showConfirmDialog(
    '確認',
    `この内容で報告を${formState.isNew ? '提出' : '更新'}します。よろしいですか？`
  )
  if (!confirmed) return

  try {
    if (formState.isNew) {
      await submitReport(cleanedReport)
    } else {
      await updateReport(cleanedReport)
    }
    emit('report-submitted')
  } catch (error) {
    showError('報告の提出に失敗しました。', error)
  }
}

const handleUndo = async () => {
  const confirmed = await showConfirmDialog(
    '確認',
    '変更を元に戻します。よろしいですか？'
  )
  if (!confirmed) {
    return
  }

  await fetchReport()
}

const expandFeedbackPanel = () => {
  if (formState.report.feedbacks && formState.report.feedbacks.length > 0) {
    expandedPanels.value = [0]
  }
}

onMounted(async () => {
  await fetchReport()
  expandFeedbackPanel()
  checkAndScrollToFeedback()
})
</script>

<style>
.v-expansion-panel-title {
  font-size: 1rem;
}

.v-expansion-panel-text__wrapper {
  padding: 8px 12px;
}
</style>

<style scoped>
.report-form-container {
  padding: 16px 0 32px;
}

.project-list-item:hover {
  background-color: rgba(179, 215, 255, 0.6) !important;
}

.project-delete-btn {
  opacity: 0.6;
  transition: opacity 0.2s;
}

.project-delete-btn:hover {
  opacity: 1;
}

.project-delete-btn .v-icon {
  font-size: 18px;
  color: #757575;
}

.work-item-input :deep() .v-input__append {
  padding: 0;
  margin-right: 8px;
}

.overtime-input {
  max-width: 300px;
}

.overtime-input :deep() input {
  text-align: right !important;
  font-size: 1.2em;
}

.overtime-input :deep() input::-webkit-outer-spin-button,
.overtime-input :deep() input::-webkit-inner-spin-button {
  margin-left: 10px;
}

.custom-list-subtext {
  display: block;
  text-indent: 1em;
  padding-top: 4px;
}

.custom-tooltip p {
  margin: 5px 0;
  line-height: 1.6;
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
</style>