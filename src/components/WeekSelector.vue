<template>
    <div class="calendar-container">
      <div class="calendar">
        <div class="weekdays">
          <div class="week-number-header">週</div>
          <div v-for="day in weekdays" :key="day.label" :class="day.class">{{ day.label }}</div>
        </div>
        <div class="days">
          <template v-for="(week, weekIndex) in groupedCalendarDays" :key="weekIndex">
            <div 
              class="week-number" 
              :class="{ 'selectable-week': isSelectableWeek(week[0].date) }"
              @click="selectWeek(week[0].date)"
            >
              {{ getWeekNumber(week[0].date) }}
            </div>
            <div
              v-for="day in week"
              :key="day.date.toISOString()"
              :class="[
                'day',
                { 'selected': isSelected(day.date) },
                { 'hovered': isHovered(day.date) && !isSelected(day.date) },
                { 'today': isToday(day.date) },
                { 'saturday': isSaturday(day.date) },
                { 'sunday': isSunday(day.date) },
                { 'selectable': isSelectableDate(day.date) }
              ]"
              @click="selectDate(day.date)"
              @mouseenter="setHoverWeek(day.date)"
              @mouseleave="clearHoverWeek"
            >
              {{ day.date.getDate() }}
            </div>
          </template>
        </div>
      </div>
      <div v-if="selectedWeek" class="selected-week">
        選択された週: {{ formatDateRange(selectedWeek.start, selectedWeek.end) }}
        <button @click="goToReport" class="report-button">報告する</button>
      </div>
    </div>
  </template>
  
  <script>
  import { ref, computed, onMounted } from 'vue'
  import { useRouter } from 'vue-router'
  
  export default {
    name: 'WeekSelector',
    setup() {
      const router = useRouter()
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      const fourWeeksAgo = new Date(today.getFullYear(), today.getMonth(), today.getDate() - 27)
      const selectedWeek = ref(null)
      const hoverWeek = ref(null)
      const weekdays = [
        { label: '月', class: '' },
        { label: '火', class: '' },
        { label: '水', class: '' },
        { label: '木', class: '' },
        { label: '金', class: '' },
        { label: '土', class: 'saturday' },
        { label: '日', class: 'sunday' }
      ]
  
      const calendarDays = computed(() => {
        const days = []
        const startDate = getWeekRange(fourWeeksAgo).start
        for (let i = 0; i < 28; i++) {
          const date = new Date(startDate.getFullYear(), startDate.getMonth(), startDate.getDate() + i)
          days.push({ date })
        }
        return days
      })
  
      const groupedCalendarDays = computed(() => {
        const grouped = []
        for (let i = 0; i < calendarDays.value.length; i += 7) {
          grouped.push(calendarDays.value.slice(i, i + 7))
        }
        return grouped
      })
  
      const getWeekRange = (date) => {
        const day = date.getDay()
        const diff = date.getDate() - day + (day === 0 ? -6 : 1) // 月曜日を週の始まりとする調整
        const weekStart = new Date(date.getFullYear(), date.getMonth(), diff)
        weekStart.setHours(0, 0, 0, 0)
        const weekEnd = new Date(weekStart.getFullYear(), weekStart.getMonth(), weekStart.getDate() + 6)
        weekEnd.setHours(23, 59, 59, 999)
        return { start: weekStart, end: weekEnd }
      }
  
      const getWeekNumber = (date) => {
        const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()))
        const dayNum = d.getUTCDay() || 7
        d.setUTCDate(d.getUTCDate() + 4 - dayNum)
        const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1))
        return Math.ceil((((d - yearStart) / 86400000) + 1) / 7)
      }
  
      const selectDate = (date) => {
        if (isSelectableDate(date)) {
          selectedWeek.value = getWeekRange(date)
        }
      }
  
      const selectWeek = (date) => {
        if (isSelectableWeek(date)) {
          const weekRange = getWeekRange(date)
          const start = new Date(Math.max(weekRange.start.getTime(), fourWeeksAgo.getTime()))
          const end = new Date(Math.min(weekRange.end.getTime(), today.getTime()))
          selectedWeek.value = { start, end }
        }
      }
  
      const isSelected = (date) => {
        if (!selectedWeek.value) return false
        return date >= selectedWeek.value.start && date <= selectedWeek.value.end
      }
  
      const isToday = (date) => {
        return date.toDateString() === today.toDateString()
      }
  
      const setHoverWeek = (date) => {
        if (isSelectableDate(date) && !isSelected(date)) {
          hoverWeek.value = getWeekRange(date)
        }
      }
  
      const clearHoverWeek = () => {
        hoverWeek.value = null
      }
  
      const isHovered = (date) => {
        if (!hoverWeek.value) return false
        return date >= hoverWeek.value.start && date <= hoverWeek.value.end
      }
  
      const isSaturday = (date) => {
        return date.getDay() === 6
      }
  
      const isSunday = (date) => {
        return date.getDay() === 0
      }
  
      const isSelectableDate = (date) => {
        return date >= fourWeeksAgo && date <= today
      }
  
      const isSelectableWeek = (date) => {
        const weekRange = getWeekRange(date)
        return weekRange.start <= today && weekRange.end >= fourWeeksAgo
      }
  
      const formatDateRange = (start, end) => {
        const options = { month: 'long', day: 'numeric' }
        return `${start.toLocaleDateString('ja-JP', options)} - ${end.toLocaleDateString('ja-JP', options)}`
      }
  
      const setDefaultWeek = () => {
        const todayDay = today.getDay()
        let defaultDate
  
        if (todayDay >= 1 && todayDay <= 5) {
          // 月曜日から金曜日の場合、前の週を選択
          defaultDate = new Date(today.getFullYear(), today.getMonth(), today.getDate() - 7)
        } else {
          // 土曜日か日曜日の場合、現在の週を選択
          defaultDate = today
        }
  
        selectWeek(defaultDate)
      }
  
      const goToReport = () => {
        if (selectedWeek.value) {
          router.push({
            name: 'WeeklyReport',
            params: { 
              startDate: selectedWeek.value.start.toISOString().split('T')[0],
              endDate: selectedWeek.value.end.toISOString().split('T')[0]
            }
          })
        }
      }
  
      onMounted(() => {
        setDefaultWeek()
      })
  
      return {
        weekdays,
        groupedCalendarDays,
        selectedWeek,
        selectDate,
        selectWeek,
        isSelected,
        isToday,
        setHoverWeek,
        clearHoverWeek,
        isHovered,
        isSaturday,
        isSunday,
        isSelectableDate,
        isSelectableWeek,
        formatDateRange,
        getWeekNumber,
        goToReport
      }
    }
  }
  </script>
  
  <style scoped>
  .calendar-container {
    max-width: 800px;
    margin: 0 auto;
    font-family: Arial, sans-serif;
    background-color: #ffffff;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    border-radius: 8px;
    padding: 20px;
  }
  
  .calendar {
    border: 1px solid #e0e0e0;
    border-radius: 5px;
    overflow: hidden;
  }
  
  .weekdays, .days {
    display: grid;
    grid-template-columns: 40px repeat(7, 1fr);
  }
  
  .weekdays {
    background-color: #f8f9fa;
    border-bottom: 1px solid #e0e0e0;
  }
  
  .weekdays div {
    text-align: center;
    font-weight: bold;
    padding: 12px 0;
    color: #495057;
  }
  
  .week-number-header, .week-number {
    background-color: #f1f3f5;
    display: flex;
    justify-content: center;
    align-items: center;
    font-weight: bold;
    color: #6c757d;
    border-right: 1px solid #e0e0e0;
  }
  
  .week-number-header {
    border-bottom: 1px solid #e0e0e0;
  }
  
  .week-number.selectable-week {
    cursor: pointer;
    transition: background-color 0.2s ease;
  }
  
  .week-number.selectable-week:hover {
    background-color: #e9ecef;
  }
  
  .day {
    padding: 12px;
    text-align: center;
    transition: all 0.2s ease;
    color: #495057;
    border: none;
  }
  
  .day.selectable {
    cursor: pointer;
  }
  
  .day.hovered {
    background-color: #e9ecef;
  }
  
  .day.selected {
    background-color: #007bff;
    color: #ffffff;
    font-weight: bold;
  }
  
  .day.selected:first-child {
    border-top-left-radius: 4px;
    border-bottom-left-radius: 4px;
  }
  
  .day.selected:last-child {
    border-top-right-radius: 4px;
    border-bottom-right-radius: 4px;
  }
  
  .day.today {
    font-weight: bold;
    position: relative;
  }
  
  .day.today::after {
    content: "";
    position: absolute;
    bottom: 4px;
    left: 50%;
    transform: translateX(-50%);
    width: 4px;
    height: 4px;
    background-color: #007bff;
    border-radius: 50%;
  }
  
  .day.saturday, .weekdays .saturday {
    color: #0000FF;
  }
  
  .day.sunday, .weekdays .sunday {
    color: #FF0000;
  }
  
  .selected-week {
    margin-top: 20px;
    text-align: center;
    font-weight: bold;
    color: #495057;
    background-color: #e9ecef;
    padding: 10px;
    border-radius: 5px;
  }
  
  .report-button {
    margin-left: 10px;
    padding: 5px 10px;
    background-color: #28a745;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }
  </style>