<template>
    <div class="report-container">
      <h2>週次報告: {{ formatDateRange(startDate, endDate) }}</h2>
      <form @submit.prevent="submitReport">
        <div v-for="(project, projectIndex) in report.projects" :key="projectIndex" class="project-section">
          <div class="form-group">
            <label :for="`project-${projectIndex}`">プロジェクト:</label>
            <select :id="`project-${projectIndex}`" v-model="project.name" required>
              <option value="">選択してください</option>
              <option value="project1">プロジェクト1</option>
              <option value="project2">プロジェクト2</option>
              <option value="project3">プロジェクト3</option>
            </select>
            <button type="button" @click="removeProject(projectIndex)" class="remove-button" v-if="report.projects.length > 1">プロジェクトを削除</button>
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
        <button type="button" @click="addProject" class="add-button">プロジェクトを追加</button>
        <div class="form-group">
          <label for="overtimeHours">残業時間:</label>
          <input type="number" id="overtimeHours" v-model="report.overtimeHours" min="0" step="0.5" required>
        </div>
        <div class="form-group">
          <label for="issues">問題点など:</label>
          <textarea id="issues" v-model="report.issues"></textarea>
        </div>
        <div class="button-group">
          <button type="button" class="back-button" @click="goBack">週選択に戻る</button>
          <button type="submit" class="submit-button">報告を提出</button>
        </div>
      </form>
    </div>
  </template>
  
  <script>
  import { ref } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  
  export default {
    name: 'WeeklyReport',
    setup() {
      const route = useRoute()
      const router = useRouter()
      const startDate = new Date(route.params.startDate)
      const endDate = new Date(route.params.endDate)
  
      const report = ref({
        projects: [{ name: '', workItems: [{ content: '' }] }],
        overtimeHours: 0,
        issues: ''
      })
  
      const formatDateRange = (start, end) => {
        const options = { month: 'long', day: 'numeric' }
        return `${start.toLocaleDateString('ja-JP', options)} - ${end.toLocaleDateString('ja-JP', options)}`
      }
  
      const addProject = () => {
        report.value.projects.push({ name: '', workItems: [{ content: '' }] })
      }
  
      const removeProject = (index) => {
        report.value.projects.splice(index, 1)
      }
  
      const addWorkItem = (project) => {
        project.workItems.push({ content: '' })
      }
  
      const removeWorkItem = (project, index) => {
        project.workItems.splice(index, 1)
        if (project.workItems.length === 0) {
          addWorkItem(project)
        }
      }
  
      const submitReport = () => {
        // ここで報告を送信する処理を実装
        console.log('Report submitted:', report.value)
        // 送信後、カレンダー画面に戻る
        router.push('/')
      }
  
      const goBack = () => {
        router.push('/')
      }
  
      return {
        startDate,
        endDate,
        report,
        formatDateRange,
        addProject,
        removeProject,
        addWorkItem,
        removeWorkItem,
        submitReport,
        goBack
      }
    }
  }
  </script>
  
  <style scoped>
  .report-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
    background-color: #ffffff;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    border-radius: 8px;
  }
  
  h2 {
    text-align: center;
    margin-bottom: 20px;
    color: #333;
  }
  
  .project-section {
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 15px;
    margin-bottom: 20px;
  }
  
  .form-group {
    margin-bottom: 20px;
  }
  
  label {
    display: block;
    margin-bottom: 5px;
    font-weight: bold;
    color: #555;
  }
  
  input, select, textarea {
    width: 100%;
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
  }
  
  textarea {
    height: 100px;
    resize: vertical;
  }
  
  .work-item {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
  }
  
  .work-item input {
    flex-grow: 1;
    margin-right: 5px;
  }
  
  .remove-button {
    background: none;
    border: none;
    font-size: 16px;
    cursor: pointer;
    padding: 0 5px;
    color: #999;
    transition: color 0.2s ease;
  }
  
  .remove-button:hover {
    color: #333;
  }
  
  .add-button {
    background-color: #28a745;
    color: white;
    border: none;
    padding: 5px 10px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
    transition: background-color 0.2s ease;
    margin-top: 10px;
  }
  
  .add-button:hover {
    background-color: #218838;
  }
  
  .button-group {
    display: flex;
    justify-content: space-between;
    margin-top: 20px;
  }
  
  .back-button, .submit-button {
    padding: 10px 20px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 16px;
    transition: background-color 0.2s ease;
  }
  
  .back-button {
    background-color: #6c757d;
    color: white;
  }
  
  .back-button:hover {
    background-color: #5a6268;
  }
  
  .submit-button {
    background-color: #007bff;
    color: white;
  }
  
  .submit-button:hover {
    background-color: #0056b3;
  }
  </style>