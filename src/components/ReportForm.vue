<template>
  <v-container class="report-form-container">
    <template v-if="isLoading">
      <v-skeleton-loader
        elevation="4"
        type="text, sentences@2, actions, chip, divider, list-item-three-line, list-item@2, button"
      ></v-skeleton-loader>
    </template>

    <template v-else>
      <template v-if="showCopyButton">
        <v-expand-transition>
          <v-card 
            class="mb-4"
            elevation="4"
            color="blue-lighten-5"
          >
            <v-card-title>前週の報告内容</v-card-title>
            <v-card-text>
              <v-list class="bg-transparent custom-list">
                <v-list-item v-for="(project, index) in previousWeekReport.projects" :key="index">
                  <v-list-item-title>{{ project.name }}</v-list-item-title>
                  <v-list-item-subtitle style="display: block;">
                    <ul class="work-items-list">
                      <li v-for="(item, itemIndex) in project.workItems" :key="itemIndex">
                        {{ item.content }}
                      </li>
                    </ul>
                  </v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </v-card-text>
            <v-card-actions class="justify-end">
              <v-btn
                color="secondary"
                variant="elevated" 
                class="mx-2 mb-2"
                @click="copyFromPreviousWeek"
              >
                <v-icon
                  class="mr-1"
                  left
                >
                  mdi-content-copy
                </v-icon>
                作業内容をコピー
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-expand-transition>
      </template>

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
                  class="project-combobox"
                  label="プロジェクト"
                  required
                  dense
                  hide-details="auto"
                  @keydown="handleProjectKeydown($event, project)"
                  @update:model-value="handleProjectUpdate(project)"
                >
                  <template #item="{ props: itemProps, item }">
                    <v-list-item v-bind="itemProps" class="project-list-item">
                      <template #append>
                        <v-btn
                          icon="mdi-close"
                          size="small"
                          flat
                          @click.stop="removeProjectOption(item.title)"
                        ></v-btn>
                      </template>
                    </v-list-item>
                  </template>
                </v-combobox>
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
    </template>
  </v-container>
</template>

<script setup>
import { ref, computed, nextTick, reactive, onMounted } from 'vue'
import { getReport, submitReport } from '../services/reportService'
import { getMemberProjects, updateMemberProjects } from '../services/memberService'

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
const showCopyButton = ref(false)

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
    showCopyButton.value = false
  }
}

const addProject = () => {
  report.value.projects.push({ name: '', workItems: [] })
}

const removeProject = (projectIndex) => {
  if (report.value.projects.length > 1) {
    report.value.projects.splice(projectIndex, 1)
  } else {
    report.value.projects[0] = { name: '', workItems: [{ content: '' }] }
  }
}

const handleProjectKeydown = (event, project) => {
  if (event.key === 'Enter' && !event.isComposing) {
    event.preventDefault()
    onProjectSelect(project)
  }
}

const handleProjectUpdate = (project) => {
  if (project.workItems.length === 0) {
    project.workItems.push({ content: '' })
  }
}

const onProjectSelect = async (project) => {
  if (project.name && !projectNames.value.includes(project.name)) {
    projectNames.value.push(project.name)
    try {
      await updateMemberProjects(props.memberUuid, projectNames.value)
    } catch (error) {
      console.error('Failed to update member projects:', error)
      // オプション: エラーメッセージを表示するなどのエラーハンドリング
    }
  }
}

const removeProjectOption = async (projectToRemove) => {
  projectNames.value = projectNames.value.filter(p => p !== projectToRemove)
  // 現在選択されているプロジェクトが削除された場合、そのプロジェクトの名前をクリアする
  report.value.projects.forEach(project => {
    if (project.name === projectToRemove) {
      project.name = ''
    }
  })
  try {
    await updateMemberProjects(props.memberUuid, projectNames.value)
  } catch (error) {
    console.error('Failed to update member projects after removal:', error)
    // オプション: エラーメッセージを表示するなどのエラーハンドリング
  }
}

const getPreviousWeekString = (weekString) => {
  const [year, week] = weekString.split('-W').map(Number)
  if (week === 1) {
    return `${year - 1}-W52`
  }
  return `${year}-W${(week - 1).toString().padStart(2, '0')}`
}

const fetchReport = async () => {
  isLoading.value = true
  error.value = null
  try {
    const [fetchedReport, memberProjects] = await Promise.all([
      getReport(props.memberUuid, props.weekString),
      getMemberProjects(props.memberUuid)
    ])

    if (fetchedReport) {
      report.value = {
        ...fetchedReport,
        issues: fetchedReport.issues || '',
        achievements: fetchedReport.achievements || '',
        improvements: fetchedReport.improvements || ''
      }
    } else {
      // 今週の報告が取得できなかった場合、前週の報告を取得
      const previousWeekString = getPreviousWeekString(props.weekString)
      previousWeekReport.value = await getReport(props.memberUuid, previousWeekString)
      if (previousWeekReport.value) {
        showCopyButton.value = true
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
</style>