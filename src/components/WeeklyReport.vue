<template>
  <div class="weekly-report-container">
    <div class="week-selector">
      <h3>週の選択</h3>
      <div class="calendar">
        <div class="weekdays">
          <div class="week-number-header">週</div>
          <div v-for="day in weekdays" :key="day.label" :class="day.class">{{ day.label }}</div>
        </div>
        <div class="days">
          <template v-for="(week, weekIndex) in calendarWeeks" :key="weekIndex">
            <div 
              class="week-number" 
              :class="{ 'selectable-week': isSelectableWeek(week[0].date) }"
              @click="selectWeek(week[0].date)"
              @mouseenter="setHoverWeek(week[0].date)"
              @mouseleave="clearHoverWeek"
            >
              {{ getWeekNumber(week[0].date) }}
            </div>
            <div
              v-for="(day, dayIndex) in week"
              :key="day.date.toISOString()"
              :class="[
                'day',
                { 'selected': isSelected(day.date) },
                { 'hovered': isHovered(day.date) },
                { 'today': isToday(day.date) },
                { 'selectable': isSelectableDate(day.date) },
                { 'saturday': isSaturday(day.date) },
                { 'sunday': isSunday(day.date) }
              ]"
              @click="selectDate(day.date)"
              @mouseenter="setHoverWeek(day.date)"
              @mouseleave="clearHoverWeek"
            >
              <span v-if="shouldShowMonth(day.date, weekIndex, dayIndex)" class="month">
                {{ formatShortMonth(day.date) }}
              </span>
              <span class="date">{{ day.date.getDate() }}</span>
            </div>
          </template>
        </div>
      </div>
    </div>

    <div v-if="selectedWeek" class="report-form">
      <h2>週次報告: {{ formatDateRange(selectedWeek.start, selectedWeek.end) }}</h2>
      <form @submit.prevent="submitReport">
        <div v-for="(project, projectIndex) in report.projects" :key="projectIndex" class="project-section">
          <div class="project-header">
            <div class="form-group project-name">
              <label :for="`project-${projectIndex}`">プロジェクト:</label>
              <select :id="`project-${projectIndex}`" v-model="project.name" required>
                <option value="">選択してください</option>
                <option value="project1">プロジェクト1</option>
                <option value="project2">プロジェクト2</option>
                <option value="project3">プロジェクト3</option>
              </select>
            </div>
            <button type="button" @click="removeProject(projectIndex)" class="remove-button" v-if="report.projects.length > 1">
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
          <input type="number" id="overtimeHours" v-model="report.overtimeHours" min="0" step="0.5" required>
          <span class="time-unit">時間</span>
        </div>
        <div class="form-group">
          <label for="issues">問題点など:</label>
          <textarea id="issues" v-model="report.issues"></textarea>
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

export default {
  name: 'WeeklyReport',
  setup() {
    const selectedWeek = ref(null)
    const hoverWeek = ref(null)
    const report = ref({
      projects: [{ name: '', workItems: [{ content: '' }] }],
      overtimeHours: 0,
      issues: ''
    })

    const weekdays = [
      { label: '月', class: '' },
      { label: '火', class: '' },
      { label: '水', class: '' },
      { label: '木', class: '' },
      { label: '金', class: '' },
      { label: '土', class: 'saturday' },
      { label: '日', class: 'sunday' }
    ]

    const calendarWeeks = computed(() => {
      const weeks = []
      const today = new Date()
      const startDate = new Date(today.getFullYear(), today.getMonth(), today.getDate() - 28)
      startDate.setDate(startDate.getDate() - startDate.getDay() + 1) // 月曜日から開始

      for (let i = 0; i < 5; i++) {
        const week = []
        for (let j = 0; j < 7; j++) {
          const date = new Date(startDate)
          week.push({ date })
          startDate.setDate(startDate.getDate() + 1)
        }
        weeks.push(week)
      }
      return weeks
    })

    const selectWeek = (date) => {
      if (isSelectableWeek(date)) {
        selectedWeek.value = getWeekRange(date)
      }
    }

    const selectDate = (date) => {
      if (isSelectableDate(date)) {
        selectedWeek.value = getWeekRange(date)
      }
    }

    const setHoverWeek = (date) => {
      hoverWeek.value = getWeekRange(date)
    }

    const clearHoverWeek = () => {
      hoverWeek.value = null
    }

    const getWeekRange = (date) => {
      const start = new Date(date)
      start.setDate(start.getDate() - start.getDay() + 1)
      const end = new Date(start)
      end.setDate(end.getDate() + 6)
      return { start, end }
    }

    const isSelected = (date) => {
      if (!selectedWeek.value) return false
      return date >= selectedWeek.value.start && date <= selectedWeek.value.end
    }

    const isHovered = (date) => {
      if (!hoverWeek.value) return false
      return date >= hoverWeek.value.start && date <= hoverWeek.value.end
    }

    const isToday = (date) => {
      const today = new Date()
      return date.toDateString() === today.toDateString()
    }

    const isSelectableDate = (date) => {
      const today = new Date()
      const fourWeeksAgo = new Date(today.getFullYear(), today.getMonth(), today.getDate() - 28)
      return date >= fourWeeksAgo && date <= today
    }

    const isSelectableWeek = (date) => {
      const weekRange = getWeekRange(date)
      return isSelectableDate(weekRange.start) || isSelectableDate(weekRange.end)
    }

    const isSaturday = (date) => {
      return date.getDay() === 6
    }

    const isSunday = (date) => {
      return date.getDay() === 0
    }

    const getWeekNumber = (date) => {
      const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()))
      const dayNum = d.getUTCDay() || 7
      d.setUTCDate(d.getUTCDate() + 4 - dayNum)
      const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1))
      return Math.ceil((((d - yearStart) / 86400000) + 1) / 7)
    }

    const formatDateRange = (start, end) => {
      const options = { year: 'numeric', month: 'long', day: 'numeric' }
      return `${start.toLocaleDateString('ja-JP', options)} - ${end.toLocaleDateString('ja-JP', options)}`
    }

    const formatShortMonth = (date) => {
      return date.toLocaleDateString('ja-JP', { month: 'short' })
    }

    const shouldShowMonth = (date, weekIndex, dayIndex) => {
      return date.getDate() === 1 || (weekIndex === 0 && dayIndex === 0)
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
      console.log('Report submitted:', report.value)
      // ここで報告を送信する処理を実装
      // 送信後、フォームをリセットするなどの処理を行う
    }

    return {
      selectedWeek,
      hoverWeek,
      report,
      weekdays,
      calendarWeeks,
      selectWeek,
      selectDate,
      setHoverWeek,
      clearHoverWeek,
      isSelected,
      isHovered,
      isToday,
      isSelectableDate,
      isSelectableWeek,
      isSaturday,
      isSunday,
      getWeekNumber,
      formatDateRange,
      formatShortMonth,
      shouldShowMonth,
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
.weekly-report-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.week-selector {
  margin-bottom: 20px;
}

.week-selector h3 {
  margin-bottom: 10px;
}

.calendar {
  border: 1px solid #ddd;
  border-radius: 5px;
}

.weekdays, .days {
  display: grid;
  grid-template-columns: 40px repeat(7, 1fr);
}

.weekdays {
  background-color: #f0f0f0;
  font-weight: bold;
}

.weekdays > div, .week-number, .day {
  padding: 10px;
  text-align: center;
}

.week-number-header, .week-number {
  background-color: #e0e0e0;
  font-weight: bold;
}

.day {
  cursor: pointer;
  transition: background-color 0.2s ease;
  position: relative;
}

.day.hovered {
  background-color: #e6f2ff;
}

.day.selected {
  background-color: #b3d7ff;
  color: #333;
}

.day.today {
  font-weight: bold;
  color: #007bff;
}

.day.selectable {
  color: #333;
}

.day:not(.selectable) {
  color: #ccc;
  cursor: not-allowed;
}

.day.saturday, .weekdays .saturday {
  color: #0000FF;
}

.day.sunday, .weekdays .sunday {
  color: #FF0000;
}

.date {
  font-size: 1em;
}

.month {
  position: absolute;
  top: 2px;
  left: 2px;
  font-size: 0.6em;
  color: #666;
}

.report-form {
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.project-section {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  background-color: #ffffff;
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
}

input, select, textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.work-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.work-item input {
  flex-grow: 1;
  margin-right: 10px;
}

.remove-button, .add-button, .add-project-button, .submit-button {
  padding: 5px 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.remove-button {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.remove-button:hover {
  background-color: #f1b0b7;
}

.add-button, .add-project-button {
  background-color: #28a745;
  color: white;
}

.submit-button {
  background-color: #007bff;
  color: white;
  padding: 10px 20px;
  font-size: 16px;
}

.button-group {
  margin-top: 20px;
  text-align: right;
}

.overtime-input {
  display: flex;
  align-items: center;
}

.overtime-input input {
  width: 80px;
  margin-right: 10px;
}

.time-unit {
  font-size: 14px;
  color: #666;
}
</style>