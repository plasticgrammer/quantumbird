// src/composables/useCalendar.js
import { ref, computed } from 'vue'

export function useCalendar() {
  const selectedWeek = ref(null)

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

  const visibleWeeks = computed(() => {
    if (!selectedWeek.value) return calendarWeeks.value
    return calendarWeeks.value.filter(week => 
      week[0].date >= selectedWeek.value.start && week[0].date <= selectedWeek.value.end
    )
  })

  const selectWeek = (week) => {
    selectedWeek.value = week
  }

  const getWeekNumber = (date) => {
    const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()))
    const dayNum = d.getUTCDay() || 7
    d.setUTCDate(d.getUTCDate() + 4 - dayNum)
    const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1))
    return Math.ceil((((d - yearStart) / 86400000) + 1) / 7)
  }

  const shouldShowMonth = (date, weekIndex, dayIndex) => {
    if (date.getDate() === 1) return true; // 毎月1日
    if (weekIndex === 0 && dayIndex === 0) return true; // カレンダーの最初の日
    return false;
  }

  const formatShortMonth = (date) => {
    return date.toLocaleDateString('ja-JP', { month: 'short' })
  }

  const isToday = (date) => {
    const today = new Date()
    return date.toDateString() === today.toDateString()
  }

  const isSaturday = (date) => {
    return date.getDay() === 6
  }

  const isSunday = (date) => {
    return date.getDay() === 0
  }

  const getStringFromWeek = (week) => {
    const year = week[0].getFullYear()
    const weekNumber = getWeekNumber(week[0])
    return `${year}-W${weekNumber.toString().padStart(2, '0')}`
  }

  const getWeekFromString = (weekString) => {
    const [year, weekNumber] = weekString.split('-W')
    const date = new Date(year, 0, 1 + (weekNumber - 1) * 7)
    const day = date.getDay()
    const diff = date.getDate() - day + (day === 0 ? -6 : 1)
    const weekStart = new Date(date.setDate(diff))
    const weekEnd = new Date(weekStart)
    weekEnd.setDate(weekEnd.getDate() + 6)
    return [weekStart, weekEnd]
  }

  return {
    weekdays,
    calendarWeeks: visibleWeeks, // calendarWeeks を visibleWeeks に置き換え
    selectedWeek,
    selectWeek,
    getWeekNumber,
    formatShortMonth,
    isToday,
    isSaturday,
    isSunday,
    shouldShowMonth,
    getStringFromWeek,
    getWeekFromString
  }
}