<template>
  <v-container class="report-form-container">
    <v-btn @click="copyFromPreviousWeek" color="secondary" class="mb-4">前週よりコピー</v-btn>
    <v-form @submit.prevent="submitReport" class="report-form">
      <v-card v-for="(project, projectIndex) in localReport.projects" :key="projectIndex" class="mb-4">
        <v-card-text>
          <v-row align="center">
            <v-col cols="10">
              <v-combobox
                v-model="project.name"
                :items="projectNames"
                label="プロジェクト"
                @update:model-value="onProjectSelect(project)"
                required
                dense
                outlined
              ></v-combobox>
            </v-col>
            <v-col cols="2" class="d-flex justify-end">
              <v-btn
                icon
                x-small
                @click="removeProject(projectIndex)"
                v-if="localReport.projects.length > 1"
                class="project-delete-btn"
              >
                <v-icon small>mdi-delete-outline</v-icon>
              </v-btn>
            </v-col>
          </v-row>
          <v-row v-if="project.workItems.length > 0">
            <v-col cols="12">
              <div v-for="(item, itemIndex) in project.workItems" :key="itemIndex" class="mb-2">
                <v-text-field
                  v-model="item.content"
                  :label="`作業内容 ${itemIndex + 1}`"
                  dense
                  outlined
                  clearable
                  hide-details="auto"
                  :ref="el => setWorkItemRef(el, projectIndex, itemIndex)"
                  required
                  @keydown="handleKeyDown($event, project, itemIndex)"
                  @click:clear="removeWorkItem(project, itemIndex)"
                ></v-text-field>
              </div>
              <div class="d-flex justify-end">
                <v-btn
                  color="primary"
                  text
                  @click="addWorkItem(project)"
                  class="mt-2"
                >
                  作業を追加
                </v-btn>
              </div>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
      
      <div class="d-flex justify-end mb-4">
        <v-btn color="primary" @click="addProject">プロジェクトを追加</v-btn>
      </div>
      
      <v-row>
        <v-col cols="12" sm="6">
          <v-text-field
            v-model="formattedOvertimeHours"
            label="残業時間"
            type="number"
            min="0"
            max="99"
            step="0.5"
            @input="updateOvertime"
            required
            outlined
            dense
          >
            <template v-slot:append>
              <v-btn icon small @click="decreaseOvertime"><v-icon>mdi-minus</v-icon></v-btn>
              <v-btn icon small @click="increaseOvertime"><v-icon>mdi-plus</v-icon></v-btn>
            </template>
          </v-text-field>
        </v-col>
      </v-row>
      
      <v-textarea
        v-model="localReport.issues"
        label="報告事項（問題点など）"
        required
        rows="4"
        auto-grow
        outlined
        clear-icon="mdi-close-circle"
        clearable 
      ></v-textarea>
      
      <v-text-field
        v-model="localReport.achievements"
        label="成果"
        outlined
        dense
        clear-icon="mdi-close-circle"
        clearable 
      ></v-text-field>
      
      <v-text-field
        v-model="localReport.improvements"
        label="改善点"
        outlined
        dense
        clear-icon="mdi-close-circle"
        clearable 
      ></v-text-field>

      <v-btn color="success" type="submit" class="mt-4">報告を提出</v-btn>
    </v-form>
  </v-container>
</template>

<script>
import { ref, computed, nextTick, reactive } from 'vue'
import { useReport } from '../composables/useReport'

export default {
  name: 'ReportForm',
  props: {
    selectedWeek: {
      type: Object,
      required: true
    },
    report: {
      type: Object,
      required: true
    },
    previousWeekReport: {
      type: Object,
      default: () => ({})
    }
  },
  emits: ['update:report', 'submit-report'],
  setup(props, { emit }) {
    const { formatDateRange } = useReport()

    const localReport = ref({
      ...props.report,
      issues: props.report.issues || '',
      achievements: props.report.achievements || '',
      improvements: props.report.improvements || ''
    })
    const workItemRefs = reactive({})
    const projectNames = ref(['プロジェクト1', 'プロジェクト2', 'プロジェクト3'])

    const formattedOvertimeHours = computed({
      get: () => localReport.value.overtimeHours.toFixed(1),
      set: (value) => {
        localReport.value.overtimeHours = parseFloat(value)
      }
    })

    const updateOvertime = (event) => {
      let value = parseFloat(event.target.value)
      if (isNaN(value)) value = 0
      value = Math.max(0, Math.min(99, value))
      localReport.value.overtimeHours = parseFloat(value.toFixed(1))
      emit('update:report', { ...localReport.value })
    }

    const increaseOvertime = () => {
      if (localReport.value.overtimeHours < 99) {
        localReport.value.overtimeHours = parseFloat((localReport.value.overtimeHours + 0.5).toFixed(1))
        emit('update:report', { ...localReport.value })
      }
    }

    const decreaseOvertime = () => {
      if (localReport.value.overtimeHours > 0) {
        localReport.value.overtimeHours = parseFloat((localReport.value.overtimeHours - 0.5).toFixed(1))
        emit('update:report', { ...localReport.value })
      }
    }

    const addProject = () => {
      localReport.value.projects.push({ name: '', workItems: [] })
      emit('update:report', { ...localReport.value })
    }

    const removeProject = (index) => {
      localReport.value.projects.splice(index, 1)
      emit('update:report', { ...localReport.value })
    }
    
    const setWorkItemRef = (el, projectIndex, itemIndex) => {
      if (!workItemRefs[projectIndex]) {
        workItemRefs[projectIndex] = {}
      }
      workItemRefs[projectIndex][itemIndex] = el
    }

    const handleKeyDown = async (event, project, itemIndex) => {
      if (event.key === 'Enter' && !event.isComposing) {
        event.preventDefault();
        if (project.workItems[itemIndex].content.trim() !== '') {
          await addWorkItem(project);
          focusNewWorkItem(project, itemIndex + 1);
        }
      }
    };

    const addWorkItem = async (project) => {
      project.workItems.push({ content: '' });
      emit('update:report', { ...localReport.value });
      await nextTick();
    };

    const focusNewWorkItem = (project, newIndex) => {
      const projectIndex = localReport.value.projects.indexOf(project);
      nextTick(() => {
        if (workItemRefs[projectIndex] && workItemRefs[projectIndex][newIndex]) {
          workItemRefs[projectIndex][newIndex].focus();
        }
      });
    };

    const removeWorkItem = (project, index) => {
      project.workItems.splice(index, 1);
      if (project.workItems.length === 0) {
        addWorkItem(project);
      }
      emit('update:report', { ...localReport.value });
    };

    const copyFromPreviousWeek = () => {
      if (props.previousWeekReport) {
        localReport.value = {
          ...localReport.value,
          projects: props.previousWeekReport.projects?.map(project => ({
            ...project,
            workItems: project.workItems.map(item => ({ ...item }))
          })) || [],
          issues: props.previousWeekReport.issues || '',
          achievements: props.previousWeekReport.achievements || '',
          improvements: props.previousWeekReport.improvements || ''
        }
        emit('update:report', { ...localReport.value })
      }
    }

    const onProjectSelect = (project) => {
      if (!projectNames.value.includes(project.name)) {
        projectNames.value.push(project.name)
      }
      if (project.workItems.length === 0) {
        project.workItems.push({ content: '' })
      }
      emit('update:report', { ...localReport.value })
    }

    const submitReport = () => {
      emit('submit-report', { ...localReport.value })
    }

    return {
      localReport,
      projectNames,
      formatDateRange,
      formattedOvertimeHours,
      updateOvertime,
      increaseOvertime,
      decreaseOvertime,
      addProject,
      removeProject,
      setWorkItemRef,
      handleKeyDown,
      addWorkItem,
      removeWorkItem,
      onProjectSelect,
      submitReport,
      copyFromPreviousWeek
    }
  }
}
</script>

<style scoped>
.report-form-container {
  max-width: 960px;
  margin: 0 auto;
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
</style>