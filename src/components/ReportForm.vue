<template>
  <v-container class="report-form-container">
    <v-btn
      color="secondary"
      class="mb-4"
      @click="copyFromPreviousWeek"
    >
      <v-icon
        class="mr-1"
        left
      >
        mdi-content-copy
      </v-icon>
      前週よりコピー
    </v-btn>
    <v-form
      class="report-form elevation-4"
      @submit.prevent="handleSubmit"
    >
      <v-card
        v-for="(project, projectIndex) in report.projects"
        :key="projectIndex" 
        elevation="2"
        class="mb-4"
      >
        <v-card-text>
          <v-row align="center">
            <v-col cols="10">
              <v-combobox
                v-model="project.name"
                :items="projectNames"
                label="プロジェクト"
                required
                dense
                outlined
                hide-details="auto"
                @update:model-value="onProjectSelect(project)"
              />
            </v-col>
            <v-col
              cols="2"
              class="d-flex justify-end"
            >
              <v-btn
                v-if="report.projects.length > 1"
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
          color="primary"
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
      />
      
      <v-text-field
        v-model="report.achievements"
        label="成果"
        outlined
        dense
        clear-icon="mdi-close-circle"
        clearable 
      />
      
      <v-text-field
        v-model="report.improvements"
        label="改善点"
        outlined
        dense
        clear-icon="mdi-close-circle"
        clearable 
      />

      <v-btn
        color="success"
        type="submit"
        class="mt-4"
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
  </v-container>
</template>

<script setup>
import { ref, computed, nextTick, reactive, onMounted } from 'vue'
import { getReport, submitReport } from '../services/reportService'

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
const projectNames = ref(['プロジェクト1', 'プロジェクト2', 'プロジェクト3'])
const isLoading = ref(false)
const error = ref(null)

const formattedOvertimeHours = computed({
  get: () => report.value.overtimeHours.toFixed(1),
  set: (value) => {
    report.value.overtimeHours = parseFloat(value)
  }
})

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

const addProject = () => {
  report.value.projects.push({ name: '', workItems: [] })
}

const removeProject = (index) => {
  report.value.projects.splice(index, 1)
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
  if (props.previousWeekReport) {
    report.value = {
      ...report.value,
      projects: props.previousWeekReport.projects?.map(project => ({
        ...project,
        workItems: project.workItems.map(item => ({ ...item }))
      })) || [],
      issues: props.previousWeekReport.issues || '',
      achievements: props.previousWeekReport.achievements || '',
      improvements: props.previousWeekReport.improvements || ''
    }
  }
}

const onProjectSelect = (project) => {
  if (!projectNames.value.includes(project.name)) {
    projectNames.value.push(project.name)
  }
  if (project.workItems.length === 0) {
    project.workItems.push({ content: '' })
  }
}

const fetchReport = async () => {
  isLoading.value = true
  error.value = null
  try {
    const fetchedReport = await getReport(props.memberUuid, props.weekString)
    if (fetchedReport) {
      report.value = {
        ...fetchedReport,
        issues: fetchedReport.issues || '',
        achievements: fetchedReport.achievements || '',
        improvements: fetchedReport.improvements || ''
      }
    }
  } catch (err) {
    console.error('Failed to fetch report:', err)
    error.value = '報告書の取得に失敗しました。'
  } finally {
    isLoading.value = false
  }
}

onMounted(fetchReport)

const handleSubmit = async () => {
  try {
    const result = await submitReport(report.value)
    console.log('Report submitted successfully:', result)
  } catch (error) {
    console.error('Failed to submit report:', error)
  }
}
</script>

<style scoped>
.report-form-container {
  max-width: 800px;
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
</style>