<template>
  <div class="report-form">
    <h2>週次報告: {{ formatDateRange(selectedWeek.start, selectedWeek.end) }}</h2>
    <form @submit.prevent="submitReport">
    <div v-for="(project, projectIndex) in localReport.projects" :key="projectIndex" class="project-section">
        <div class="project-header">
        <div class="form-group project-name">
            <label :for="`project-${projectIndex}`">プロジェクト:</label>
            <select :id="`project-${projectIndex}`" v-model="project.name" required>
            <option value="">選択してください</option>
            <option v-for="projName in projectNames" :key="projName" :value="projName">
                {{ projName }}
            </option>
            </select>
        </div>
        <button type="button" @click="removeProject(projectIndex)" class="remove-button" v-if="localReport.projects.length > 1">
            プロジェクトを削除
        </button>
        </div>
        <div class="form-group">
        <label>作業内容:</label>
        <div v-for="(item, itemIndex) in project.workItems" :key="itemIndex" class="work-item">
            <input 
            type="text" 
            v-model="item.content" 
            :placeholder="`作業内容 ${itemIndex + 1}`"
            required
            >
            <button type="button" @click="removeWorkItem(project, itemIndex)" class="remove-button" aria-label="削除">✖️</button>
        </div>
        <button type="button" @click="addWorkItem(project)" class="add-button">作業を追加</button>
        </div>
    </div>
    <button type="button" @click="addProject" class="add-project-button">プロジェクトを追加</button>
    
    <div class="form-group overtime-input">
        <label for="overtimeHours">残業時間:</label>
        <div class="overtime-controls">
        <div class="overtime-number-input">
            <input 
            type="number" 
            id="overtimeHours" 
            v-model="localReport.overtimeHours" 
            min="0" 
            max="999" 
            step="0.5" 
            required
            >
            <span class="time-unit">時間</span>
        </div>
        <input 
            type="range" 
            v-model="localReport.overtimeHours" 
            min="0" 
            max="20" 
            step="0.5"
        >
        </div>
    </div>
    <div class="form-group">
        <label for="issues">問題点など:</label>
        <textarea id="issues" v-model="localReport.issues"></textarea>
    </div>
    <div class="button-group">
        <button type="submit" class="submit-button">報告を提出</button>
    </div>
    </form>
  </div>
</template>

<script>
import { reactive, watch, onMounted } from 'vue'
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
    }
  },
  emits: ['update:report', 'submit-report'],
  setup(props, { emit }) {
    const { formatDateRange } = useReport()

    const localReport = reactive({ ...props.report })

    onMounted(() => {
      Object.assign(localReport, props.report)
    })

    watch(() => props.report, (newReport) => {
      Object.assign(localReport, newReport)
    }, { deep: true })

    const updateReport = () => {
      emit('update:report', { ...localReport })
    }

    const addProject = () => {
      localReport.projects.push({ name: '', workItems: [{ content: '' }] })
      updateReport()
    }

    const removeProject = (index) => {
      localReport.projects.splice(index, 1)
      updateReport()
    }

    const addWorkItem = (project) => {
      project.workItems.push({ content: '' })
      updateReport()
    }

    const removeWorkItem = (project, index) => {
      project.workItems.splice(index, 1)
      if (project.workItems.length === 0) {
        addWorkItem(project)
      }
      updateReport()
    }

    const submitReport = () => {
      emit('submit-report', { ...localReport })
    }

    return {
      localReport,
      formatDateRange,
      addProject,
      removeProject,
      addWorkItem,
      removeWorkItem,
      submitReport
    }
  }
}
</script>

<style scoped>
.report-form {
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

h2 {
  margin-bottom: 20px;
  color: #333;
}

.project-section {
  background-color: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 5px;
  padding: 15px;
  margin-bottom: 20px;
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.form-group {
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

.work-item {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

.work-item input {
  flex-grow: 1;
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

.overtime-number-input {
  display: flex;
  align-items: center;
}

.overtime-number-input input[type="number"] {
  width: 60px;
  text-align: right;
}

.time-unit {
  margin-left: 5px;
}

button {
  padding: 8px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.add-button, .submit-button {
  background-color: #4CAF50;
  color: white;
}

.remove-button {
  background-color: #f44336;
  color: white;
}

.add-project-button {
  background-color: #2196F3;
  color: white;
  margin-bottom: 20px;
}

button:hover {
  opacity: 0.8;
}

.submit-button {
  font-size: 16px;
  padding: 10px 20px;
  margin-top: 20px;
}
</style>