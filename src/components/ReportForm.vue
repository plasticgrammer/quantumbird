<template>
  <v-container class="report-form-container">
    <template v-if="isLoading">
      <v-skeleton-loader
        elevation="4"
        type="text, sentences@2, actions, chip, divider, list-item-three-line, list-item@2, button"
      ></v-skeleton-loader>
    </template>

    <template v-else>
      <template v-if="!!previousWeekReport">
        <v-card class="mb-4" elevation="4">
          <v-expansion-panels v-model="expandedPanel">
            <v-expansion-panel>
              <v-expansion-panel-title>
                先週の報告内容
                <template #actions>
                  <v-icon icon="mdi-chevron-down"></v-icon>
                </template>
              </v-expansion-panel-title>
              <v-expansion-panel-text class="bg-blue-lighten-5">
                <v-list class="bg-transparent custom-list">
                  <v-list-item v-for="(project, index) in previousWeekReport.projects" :key="index">
                    <v-list-item-title>
                      <v-icon small>
                        mdi-folder-outline
                      </v-icon>
                      {{ project.name }}
                    </v-list-item-title>
                    <v-list-item-subtitle>
                      <ul class="work-items-list">
                        <li v-for="(item, itemIndex) in project.workItems" :key="itemIndex">
                          {{ item.content }}
                        </li>
                      </ul>
                    </v-list-item-subtitle>
                  </v-list-item>
                  <v-list-item>
                    <v-list-item-title>現状・問題点</v-list-item-title>
                    <v-list-item-subtitle class="custom-list-subtext">
                      {{ previousWeekReport.issues }}
                    </v-list-item-subtitle>
                  </v-list-item>
                  <v-list-item>
                    <v-list-item-title>改善点</v-list-item-title>
                    <v-list-item-subtitle class="custom-list-subtext">
                      {{ previousWeekReport.improvements }}
                    </v-list-item-subtitle>
                  </v-list-item>
                </v-list>
                <v-row class="justify-end pa-4">
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

      <template
        v-if="report.status === 'feedback' && report.feedbacks"
      >
        <v-alert
          v-for="(feedback, index) in report.feedbacks" :key="index" 
          icon="mdi-message"
          density="compact"
          border="start"
          border-color="warning"
          elevation="2"
          outlined
          dense
          class="mb-2 custom-feedback-alert"
        >
          <div>
            フィードバック（{{ new Date(feedback.createdAt).toLocaleString() }}）:
          </div>
          <div class="mt-1">
            <p>{{ feedback.content }}</p>
          </div>
        </v-alert>
      </template>

      <v-form
        class="report-form mt-3 elevation-4"
        @submit.prevent="handleSubmit"
      >
        <v-card
          v-for="(project, projectIndex) in report.projects"
          :key="projectIndex" 
          elevation="4"
          class="mb-4"
        >
          <v-card-text>
            <v-row align="center">
              <v-col cols="10">
                <ProjectSelector
                  v-model="project.name"
                  :project-names="projectNames"
                  :member-uuid="props.memberUuid"
                  :error-messages="projectErrors[projectIndex]?.name"
                  @project-list-changed="updateProjectList"
                />
              </v-col>
              <v-col
                cols="2"
                class="d-flex justify-end"
              >
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
              <v-col cols="12">
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
                    class="work-item-input pl-5"
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
        
        <div class="d-flex justify-end mb-4">
          <v-btn
            color="secondary"
            @click="addProject"
          >
            <v-icon
              class="mr-1"
              left
            >
              mdi-plus
            </v-icon>
            プロジェクトを追加
          </v-btn>
        </div>
        
        <v-row>
          <v-col
            cols="12"
            sm="6"
          >
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
                  small
                  @click="decreaseOvertime"
                >
                  <v-icon>mdi-minus</v-icon>
                </v-btn>
                <v-btn
                  icon
                  small
                  @click="increaseOvertime"
                >
                  <v-icon>mdi-plus</v-icon>
                </v-btn>
              </template>
            </v-text-field>
          </v-col>
        </v-row>
        
        <v-textarea
          v-model="report.issues"
          label="現状・問題点"
          required
          rows="4"
          auto-grow
          outlined
          clear-icon="mdi-close-circle"
          clearable 
          :error-messages="formErrors.issues"
        />
        
        <v-text-field
          v-model="report.achievements"
          label="成果"
          outlined
          dense
          clear-icon="mdi-close-circle"
          clearable 
          :error-messages="formErrors.achievements"
        />
        
        <v-text-field
          v-model="report.improvements"
          label="改善点"
          outlined
          dense
          clear-icon="mdi-close-circle"
          clearable 
          :error-messages="formErrors.improvements"
        />

        <v-btn
          color="primary"
          type="submit"
          class="mt-4"
          :disabled="!isFormValid"
        >
          <v-icon
            class="mr-1"
            left
          >
            mdi-check
          </v-icon>
          報告を提出する
        </v-btn>
      </v-form>
    </template>
  </v-container>
</template>

<script setup>
import { ref, computed, nextTick, reactive, inject, onMounted } from 'vue'
import ProjectSelector from './ProjectSelector.vue'
import { getReport, submitReport } from '../services/reportService'
import { getMemberProjects } from '../services/memberService'
import { useCalendar } from '../composables/useCalendar'

const showNotification = inject('showNotification')

const { getPreviousWeekString } = useCalendar()

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

const initialReport = (organizationId, memberUuid, weekString) => ({
  organizationId,
  memberUuid,
  weekString,
  projects: [{ name: '', workItems: [{ content: '' }] }],
  overtimeHours: 0,
  issues: '',
  achievements: '',
  improvements: ''
})

const report = ref(initialReport(props.organizationId, props.memberUuid, props.weekString))
const workItemRefs = reactive({})
const projectNames = ref([])
const isLoading = ref(false)
const error = ref(null)
const previousWeekReport = ref(null)
const expandedPanel = ref(null)

const isFormValid = ref(true)
const formErrors = reactive({
  issues: []
})
const projectErrors = reactive([])

const formattedOvertimeHours = computed({
  get: () => report.value.overtimeHours.toFixed(1),
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

    if (fetchedReport) {
      report.value = {
        ...fetchedReport,
        issues: fetchedReport.issues || '',
        achievements: fetchedReport.achievements || '',
        improvements: fetchedReport.improvements || ''
      }
    }
    if (fetchedPrevReport) {
      previousWeekReport.value = {
        ...fetchedPrevReport,
        issues: fetchedPrevReport.issues || '',
        achievements: fetchedPrevReport.achievements || '',
        improvements: fetchedPrevReport.improvements || ''
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
    
    if (project.workItems.length === 0 || project.workItems.every(item => !item.content.trim())) {
      isValid = false
      projectErrors[index].workItems.push('少なくとも1つの作業内容を追加してください。')
    } else {
      project.workItems.forEach((item, itemIndex) => {
        if (!item.content.trim()) {
          isValid = false
          projectErrors[index].workItems[itemIndex] = '作業内容を入力してください。'
        }
      })
    }
  })

  // Check if issues field is not empty
  if (!report.value.issues.trim()) {
    isValid = false
    formErrors.issues.push('現状・問題点は必須入力です。')
  }

  return isValid
}

const handleSubmit = async () => {
  const isValid = validateReport()

  if (!isValid) {
    return
  }
  try {
    await submitReport(report.value)
    showNotification('週次報告を提出しました。')
  } catch (error) {
    console.error('Failed to submit report:', error)
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
  padding: 16px 0 0;
}

.project-list-item:hover {
  background-color: rgba(179, 215, 255, 0.6) !important;
}

.work-items-list {
  list-style-type: disc !important;
  padding-left: 24px !important;
  margin: 0;
}

.work-items-list li {
  padding: 4px 0;
  display: list-item !important;
}

.report-form {
  background-color: #f9f9f9;
  padding: 20px;
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

.custom-feedback-alert :deep() .v-icon {
  color: orange;
}
</style>