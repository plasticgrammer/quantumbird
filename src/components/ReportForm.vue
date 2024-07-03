<template>
  <div class="report-form">
    <form @submit.prevent="submitReport">
      <button @click="copyFromPreviousWeek" class="copy-button">前週より作業内容をコピー</button>
      <div v-for="(project, projectIndex) in localReport.projects" :key="projectIndex" class="project-section">
        <div class="project-header">
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
          <button 
            type="button" 
            @click="removeProject(projectIndex)" 
            class="icon-button"
            v-if="localReport.projects.length > 1"
            aria-label="プロジェクトを削除"
          >
            🗑️
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
                  v-if="project.workItems.length > 1"
                  type="button" 
                  @click="removeWorkItem(project, itemIndex)" 
                  class="remove-work-item-button"
                  aria-label="作業内容を削除"
                >
                  ✖️
                </button>
              </div>
            </div>
            <button type="button" @click="addWorkItem(project)" class="add-button">作業を追加</button>
          </div>
        </div>
      </div>
      <button type="button" @click="addProject" class="add-project-button">プロジェクトを追加</button>
      
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
        <label for="issues">問題点など:</label>
        <textarea id="issues" v-model="localReport.issues" rows="4"></textarea>
      </div>
      
      <div class="button-group">
        <button type="submit" class="submit-button">報告を提出</button>
      </div>
    </form>
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
.report-form {
  background-color: #ffffff;
  padding: 25px;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), 0 1px 3px rgba(0, 0, 0, 0.08);
  border: 1px solid #e0e0e0;
}

.project-section {
  background-color: #f9f9f9;
  border: 1px solid #d0d0d0;
  border-radius: 6px;
  padding: 20px;
  margin-bottom: 25px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.project-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
}

.project-header label {
  white-space: nowrap;
  color: #333;
}

.project-header select {
  flex-grow: 1;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px;
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

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
  margin-bottom: 10px;
}

.input-wrapper input {
  width: 100%;
  padding: 10px;
  padding-right: 30px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px;
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

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #444;
}

select, input[type="text"], input[type="number"], textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.2s;
}

select:focus, input:focus, textarea:focus {
  outline: none;
  border-color: #4a90e2;
}

textarea {
  resize: vertical;
  min-height: 100px;
}

.overtime-input {
  display: flex;
  align-items: center;
  gap: 10px;
}

.overtime-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.overtime-button {
  width: 30px;
  height: 30px;
  font-size: 18px;
  line-height: 1;
  padding: 0;
  background-color: #f0f0f0;
  border: 1px solid #ccc;
  border-radius: 4px;
  cursor: pointer;
  color: #333;
  transition: background-color 0.2s;
}

.overtime-button:hover {
  background-color: #e0e0e0;
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

button {
  padding: 10px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s, opacity 0.2s;
  font-weight: 600;
}

.add-button {
  background-color: #e8f5e9;
  color: #2e7d32;
  border: 1px solid #a5d6a7;
}

.add-button:hover {
  background-color: #c8e6c9;
}

.add-project-button {
  background-color: #e3f2fd;
  color: #1565c0;
  border: 1px solid #90caf9;
  margin-bottom: 20px;
}

.add-project-button:hover {
  background-color: #bbdefb;
}

.copy-button {
  background-color: #fff3e0;
  color: #e65100;
  border: 1px solid #ffcc80;
  margin-bottom: 20px;
}

.copy-button:hover {
  background-color: #ffe0b2;
}

.submit-button {
  background-color: #4caf50;
  color: white;
  font-size: 16px;
  padding: 12px 24px;
  margin-top: 20px;
}

.submit-button:hover {
  background-color: #45a049;
}

button:hover {
  opacity: 0.9;
}
</style>