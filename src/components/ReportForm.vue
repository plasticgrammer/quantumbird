<template>
  <v-container class="report-form-container">
    <template v-if="isLoading">
      <v-skeleton-loader
        elevation="4"
        type="text, sentences@2, actions, chip, divider, list-item-three-line, list-item@2, button"
      ></v-skeleton-loader>
    </template>

    <template v-else>
      <template v-if="isReportConfirmed">
        <v-alert
          type="info"
          icon="mdi-information"
          border="start"
          elevation="2"
          class="mt-2 mb-6"
        >
          この報告は確認済みです。編集はできません。
        </v-alert>
      </template>

      <template v-if="!!previousWeekReport && !isReportConfirmed">
        <v-card class="mb-4">
          <v-expansion-panels v-model="expandedPanel">
            <v-expansion-panel>
              <v-expansion-panel-title class="bg-grey-lighten-4">
                <span class="text-decoration-underline" style="text-underline-offset: 4px">
                  前週の報告内容
                </span>
                <template #actions>
                  <v-icon icon="mdi-chevron-down"></v-icon>
                </template>
              </v-expansion-panel-title>
              <v-expansion-panel-text>
                <v-row>
                  <v-col cols="12" md="5" class="pa-2">
                    <v-list class="bg-transparent custom-list">
                      <v-list-item v-for="(project, index) in previousWeekReport.projects" :key="index">
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
                      v-model="previousWeekReport.issues"
                      label="現状・問題点"
                      outlined
                      readonly
                      auto-grow
                      rows="2"
                      hide-details
                      class="small-text-area mb-2"
                    />

                    <v-textarea
                      v-model="previousWeekReport.improvements"
                      label="改善点"
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
        class="report-form mt-3 elevation-6 pa-3 pa-md-5"
        :class="{ 'form-disabled': isReportConfirmed } " 
        @submit.prevent="handleSubmit"
      >
        <!-- Projects section -->
        <v-card
          v-for="(project, projectIndex) in report.projects"
          :key="projectIndex" 
          elevation="2"
          class="pb-2 mb-4"
        >
          <v-card-text>
            <v-row>
              <v-col cols="9" class="pa-1 pa-md-4">
                <ProjectSelector
                  v-model="project.name"
                  :project-names="projectNames"
                  :member-uuid="props.memberUuid"
                  :error-messages="projectErrors[projectIndex]?.name"
                  @project-list-changed="updateProjectList"
                />
              </v-col>
              <v-col cols="3" class="d-flex justify-end">
                <v-btn
                  icon
                  x-small
                  class="project-delete-btn"
                  @click="removeProject(projectIndex)"
                >
                  <v-icon small>
                    mdi-delete-outline
                  </v-icon>
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
                    dense
                    outlined
                    hide-details="auto"
                    :error-messages="projectErrors[projectIndex]?.workItems[itemIndex]"
                    required
                    class="work-item-input pl-2 pl-md-5"
                    @keydown="handleKeyDown($event, project, itemIndex)"
                  >
                    <template #append>
                      <v-icon 
                        :color="item.content ? 'grey darken-2' : 'grey lighten-1'"
                        small
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
              label="残業時間"
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
          v-model="report.issues"
          label="現状と問題点"
          required
          rows="3"
          auto-grow
          outlined
          clear-icon="mdi-close-circle"
          clearable 
          :error-messages="formErrors.issues"
        />

        <v-text-field
          v-model="report.improvements"
          label="改善したいこと"
          outlined
          dense
          clear-icon="mdi-close-circle"
          clearable 
          :error-messages="formErrors.improvements"
        />

        <!-- Rating section -->
        <v-card 
          class="mt-2 border-sm"
          elevation="0"
          variant="flat"
          color="blue-lighten-5"
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
            />
          </v-card-text>
        </v-card>
        <div v-if="formErrors.rating.length" class="v-input--error">
          <div class="v-input__details">
            <div 
              v-for="(ratingError, index) in formErrors.rating"
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
          v-if="report.feedbacks && report.feedbacks.length"  
          class="mt-2"
        >
          <v-col cols="12">
            <v-alert
              density="compact"
              class="feedback-box px-2 pb-2"
              :class="{ 'form-disabled': isReportConfirmed } " 
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
                v-for="(feedback, index) in sortedFeedbacks"
                :key="feedback.id"
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
                <template v-if="!!feedback.replyComment || isLatestFeedback(index)">
                  <v-textarea
                    v-model="feedback.replyComment"
                    label="返信コメント"
                    :readonly="!isLatestFeedback(index)"
                    :clearable="isLatestFeedback(index)"
                    :rows="isLatestFeedback(index) ? 2 : 1"
                    auto-grow
                    hide-details
                    clear-icon="mdi-close-circle"
                    class="ml-4 mr-3"
                    :class="{ 'borderless-textarea': !isLatestFeedback(index), 'mt-n2': !isLatestFeedback(index), 'my-2': isLatestFeedback(index) }"
                  >
                    <template #prepend-inner>
                      <v-icon class="mr-1" color="grey-darken-3" size="large">
                        mdi-reply
                      </v-icon>
                    </template>
                  </v-textarea>
                </template>
              </div>
            </v-alert>
          </v-col>
        </v-row>

        <v-row class="mt-2">
          <v-col cols="12" class="d-flex justify-end">
            <v-btn
              color="primary"
              type="submit"
              :disabled="!isFormValid || isReportConfirmed"
            >
              <v-icon class="mr-1" left>
                mdi-check
              </v-icon>
              報告を{{ isNew ? '提出' : '更新' }}する
            </v-btn>
          </v-col>
        </v-row>
      </v-form>
    </template>
  </v-container>
</template>

<script setup>
import { ref, computed, nextTick, reactive, inject, onMounted } from 'vue'
import { getReport, submitReport, getMemberProjects } from '../services/publicService'
import { useCalendar } from '../composables/useCalendar'
import { useReport } from '../composables/useReport'
import { useResponsive } from '../composables/useResponsive'
import ProjectSelector from './ProjectSelector.vue'
import RatingItem from '../components/RatingItem.vue'

const { isMobile } = useResponsive()
const showNotification = inject('showNotification')

const { formatDateTimeJp, getPreviousWeekString } = useCalendar()
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

const report = ref(initialReport(props.organizationId, props.memberUuid, props.weekString))
const workItemRefs = reactive({})
const projectNames = ref([])
const isLoading = ref(false)
const isNew = ref(true)
const error = ref(null)
const previousWeekReport = ref(null)
const expandedPanel = ref(null)

const isFormValid = ref(true)
const formErrors = reactive({
  issues: [],
  rating: []
})
const projectErrors = reactive([])

const isReportConfirmed = computed(() => {
  return report.value.status === 'approved'
})

const sortedFeedbacks = computed(() => {
  return [...(report.value.feedbacks || [])].sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt))
})

const isLatestFeedback = (index) => {
  return index === report.value.feedbacks.length - 1
}

const formattedOvertimeHours = computed({
  get: () => {
    const hours = report.value?.overtimeHours ?? 0
    return hours.toFixed(1)
  },
  set: (value) => {
    report.value.overtimeHours = parseFloat(value)
  }
})

const updateProjectList = (newProjectList) => {
  projectNames.value = newProjectList
}

const updateOvertime = (event) => {
  let value = parseFloat(event.target.value)
  if (isNaN(value)) value = 0
  value = Math.max(0, Math.min(99, value))
  report.value.overtimeHours = parseFloat(value.toFixed(1))
}

const increaseOvertime = () => {
  if (report.value.overtimeHours < 99) {
    report.value.overtimeHours = parseFloat((report.value.overtimeHours + 0.5).toFixed(1))
  }
}

const decreaseOvertime = () => {
  if (report.value.overtimeHours > 0) {
    report.value.overtimeHours = parseFloat((report.value.overtimeHours - 0.5).toFixed(1))
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
    if (project.workItems[itemIndex].content.trim() !== '') {
      await addWorkItem(project)
      focusNewWorkItem(project, itemIndex + 1)
    }
  }
}

const addWorkItem = async (project) => {
  project.workItems.push({ content: '' })
  await nextTick()
}

const focusNewWorkItem = (project, newIndex) => {
  const projectIndex = report.value.projects.indexOf(project)
  nextTick(() => {
    if (workItemRefs[projectIndex] && workItemRefs[projectIndex][newIndex]) {
      workItemRefs[projectIndex][newIndex].focus()
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
  if (previousWeekReport.value) {
    report.value = {
      ...report.value,
      projects: previousWeekReport.value.projects?.map(project => ({
        ...project,
        workItems: project.workItems.map(item => ({ ...item }))
      })) || [],
    }
  }
}

const addProject = () => {
  report.value.projects.push({ name: '', workItems: [{ content: '' }] })
}

const removeProject = (projectIndex) => {
  report.value.projects.splice(projectIndex, 1)
}

const fetchReport = async () => {
  isLoading.value = true
  error.value = null
  try {
    const previousWeekString = getPreviousWeekString(props.weekString)
    const [fetchedReport, fetchedPrevReport, memberProjects] = await Promise.all([
      getReport(props.memberUuid, props.weekString),
      getReport(props.memberUuid, previousWeekString),
      getMemberProjects(props.memberUuid)
    ])

    isNew.value = true
    if (fetchedReport) {
      isNew.value = false
      report.value = {
        ...fetchedReport,
        issues: fetchedReport.issues || '',
        improvements: fetchedReport.improvements || '',
        rating: fetchedReport.rating || {}
      }
    }
    if (fetchedPrevReport) {
      previousWeekReport.value = {
        ...fetchedPrevReport,
        issues: fetchedPrevReport.issues || ' ',
        improvements: fetchedPrevReport.improvements || ' '
      }
    }
    projectNames.value = memberProjects
  } catch (err) {
    console.error('Failed to fetch report or member projects:', err)
    error.value = '報告書またはプロジェクトリストの取得に失敗しました。'
  } finally {
    isLoading.value = false
  }
}

onMounted(fetchReport)

const validateReport = () => {
  let isValid = true
  formErrors.issues = []
  formErrors.rating = []
  projectErrors.length = 0

  // Check if there's at least one project
  if (report.value.projects.length === 0) {
    isValid = false
    showNotification('少なくとも1つのプロジェクトを追加してください。', true)
  }

  // Check each project and its work items
  report.value.projects.forEach((project, index) => {
    projectErrors[index] = { name: [], workItems: [] }
    
    if (!project.name.trim()) {
      isValid = false
      projectErrors[index].name.push('プロジェクト名を入力してください。')
    }
    const validWorkItems = project.workItems.filter(item => item.content.trim() !== '')
    if (validWorkItems.length === 0) {
      isValid = false
      projectErrors[index].workItems.push('少なくとも1つの作業内容を追加してください。')
    }
  })

  // Check if issues field is not empty
  if (!report.value.issues.trim()) {
    isValid = false
    formErrors.issues.push('現状・問題点は必須入力です。')
  }

  if (!report.value.rating?.achievement || !report.value.rating?.disability || !report.value.rating?.stress) {
    isValid = false
    formErrors.rating.push('評価は必須入力です。')
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
    showNotification('確認済みの報告書は編集できません。', true)
    return
  }

  const isValid = validateReport()

  if (!isValid) {
    return
  }

  try {
    // Remove empty work items before submission
    const cleanedReport = {
      ...report.value,
      projects: removeEmptyWorkItems(report.value.projects),
      status: 'pending'
    }

    // Additional check to ensure each project has at least one work item
    if (cleanedReport.projects.some(project => project.workItems.length === 0)) {
      showNotification('各プロジェクトに少なくとも1つの作業内容が必要です。', true)
      return
    }

    await submitReport(cleanedReport)
    //showNotification('報告を提出しました。')
    emit('report-submitted')

  } catch (error) {
    console.error('Failed to submit report:', error)
    showNotification('報告の提出に失敗しました。', true)
  }
}
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

.report-form {
  background-color: #f9f9f9;
  border-radius: 8px;
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

.feedback-box {
  border: 1px solid rgb(0 0 0 / 0.2) !important;
  background-color: transparent;
}
</style>