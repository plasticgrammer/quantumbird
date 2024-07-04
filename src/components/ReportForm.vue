<template>
  <div class="report-form-container">
    <button @click="copyFromPreviousWeek" class="copy-button">前週よりコピー</button>
    <div class="report-form">
      <form @submit.prevent="submitReport">
        <div v-for="(project, projectIndex) in localReport.projects" :key="projectIndex" class="project-section">
          <div class="project-header">
            <div class="form-group project-name">
              <label :for="`project-${projectIndex}`">プロジェクト:</label>
              <select 
                :id="`project-${projectIndex}`" 
                v-model="project.name" 
                required
                @change="onProjectSelect(project)"
              >
                <option value="">選択してください</option>
                <option v-for="projName in projectNames" :key="projName" :value="projName">
                  {{ projName }}
                </option>
              </select>
            </div>
            <button 
              type="button" 
              @click="removeProject(projectIndex)" 
              class="remove-button"
              v-if="localReport.projects.length > 1"
              aria-label="プロジェクトを削除"
            >
              ×
            </button>
          </div>
          <div v-if="project.workItems.length > 0" class="work-items-section">
            <div class="form-group">
              <label>作業内容:</label>
              <div v-for="(item, itemIndex) in project.workItems" :key="itemIndex" class="work-item">
                <div class="input-wrapper">
                  <input 
                    type="text" 
                    v-model="item.content" 
                    :placeholder="`作業内容 ${itemIndex + 1}`"
                    required
                  >
                  <button 
                    type="button" 
                    @click="removeWorkItem(project, itemIndex)" 
                    class="remove-work-item-button"
                    aria-label="作業内容を削除"
                  >
                    ✖️
                  </button>
                </div>
              </div>
              <div class="button-container">
                <button type="button" @click="addWorkItem(project)" class="action-button">作業を追加</button>
              </div>
            </div>
          </div>
        </div>
        <div class="button-container">
          <button type="button" @click="addProject" class="action-button">プロジェクトを追加</button>
        </div>
        
        <div class="form-group overtime-input">
          <label for="overtimeHours">残業時間:</label>
          <div class="overtime-controls">
            <input 
              type="number" 
              id="overtimeHours" 
              v-model="formattedOvertimeHours" 
              @input="updateOvertime"
              min="0" 
              max="99" 
              step="0.5" 
              required
            >
            <span class="time-unit">時間</span>
            <button type="button" @click="decreaseOvertime" class="overtime-button">－</button>
            <button type="button" @click="increaseOvertime" class="overtime-button">＋</button>
          </div>
        </div>
        
        <div class="form-group">
          <label for="issues">報告事項（成果、問題点など）:</label>
          <textarea id="issues" v-model="localReport.issues"></textarea>
        </div>
        
        <div class="button-group">
          <button type="submit" class="submit-button">報告を提出</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
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
      projects: props.report.projects.map(project => ({
        ...project,
        workItems: project.workItems.length > 0 ? project.workItems : [{ content: '' }]
      }))
    })

    const projectNames = ['プロジェクト1', 'プロジェクト2', 'プロジェクト3']

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

    const addWorkItem = (project) => {
      project.workItems.push({ content: '' })
      emit('update:report', { ...localReport.value })
    }

    const removeWorkItem = (project, index) => {
      if (project.workItems.length > 1) {
        project.workItems.splice(index, 1)
        emit('update:report', { ...localReport.value })
      }
    }

    const copyFromPreviousWeek = () => {
      if (props.previousWeekReport && props.previousWeekReport.projects) {
        localReport.value.projects = props.previousWeekReport.projects.map(project => ({
          ...project,
          workItems: project.workItems.map(item => ({ ...item }))
        }))
        emit('update:report', { ...localReport.value })
      }
    }

    const onProjectSelect = (project) => {
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
  margin-bottom: 20px;
}

.copy-button {
  background-color: #f0f0f0;
  border: 1px solid #ccc;
  color: #333;
  padding: 10px 15px;
  border-radius: 4px;
  cursor: pointer;
  margin-bottom: 10px;
  transition: background-color 0.2s, opacity 0.2s;
}

.copy-button:hover {
  opacity: 0.8;
}

.report-form {
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.project-section {
  position: relative;
  background-color: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 5px;
  padding: 15px;
  margin-bottom: 20px;
}

.project-header {
  margin-bottom: 15px;
}

label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
  color: #555;
}

select, input[type="text"], input[type="number"], textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px;
}

textarea {
  resize: vertical;
  min-height: 6em;
  line-height: 1.5;
}

.project-name {
  flex-grow: 1;
  margin-right: 10px;
}

.icon-button {
  background-color: #f0f0f0;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 1.2em;
  cursor: pointer;
  padding: 5px 10px;
  transition: background-color 0.2s;
}

.icon-button:hover {
  background-color: #e0e0e0;
}

.work-items-section {
  margin-top: 10px;
}

.work-item {
  margin-bottom: 10px;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-wrapper input {
  flex-grow: 1;
  padding-right: 30px;
}

.remove-work-item-button {
  position: absolute;
  right: 5px;
  background: none;
  border: none;
  font-size: 1em;
  cursor: pointer;
  padding: 5px;
  color: #999;
}

.remove-work-item-button:hover {
  color: #666;
}

.button-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 10px;
}

.action-button,
.overtime-button {
  width: auto;
  height: auto;
  font-size: 14px;
  line-height: 1;
  padding: 8px 12px;
  background-color: #f0f0f0;
  border: 1px solid #ccc;
  border-radius: 4px;
  cursor: pointer;
  color: #333;
  transition: background-color 0.2s;
}

.action-button:hover,
.overtime-button:hover {
  background-color: #e0e0e0;
}

.remove-button {
  position: absolute;
  top: 10px;
  right: 10px;
  font-size: 18px;
  padding: 4px 8px;
  background-color: #f0f0f0;
  border: 1px solid #ccc;
  border-radius: 4px;
  cursor: pointer;
  color: #333;
  transition: background-color 0.2s;
}

.remove-button:hover {
  background-color: #e0e0e0;
}

.overtime-input {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
}

.overtime-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.overtime-controls input[type="number"] {
  width: 60px;
  text-align: center;
  font-size: 16px;
}

.time-unit {
  font-size: 14px;
  color: #666;
}

textarea {
  box-sizing: border-box;
  resize: vertical;
  min-height: 80px;
}

.submit-button {
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 10px 20px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.2s;
  margin-top: 20px;
}

.submit-button:hover {
  background-color: #45a049;
}
</style>