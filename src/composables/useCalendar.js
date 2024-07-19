// src/composables/useCalendar.js
import { ref, computed } from 'vue'

export function useCalendar() {
  const selectedWeek = ref(null)

  const calendarWeeks = computed(() => {
    const weeks = [];
    const today = new Date();
    const weekCount = 6;

    let currentDate = new Date(today.getFullYear(), today.getMonth(), today.getDate() - 7 * (weekCount - 1));

    // 最初の月曜日まで移動
    while (currentDate.getDay() !== 1) {
      currentDate.setDate(currentDate.getDate() - 1);
    }

    for (let i = 0; i < weekCount; i++) {
      const week = [];
      for (let j = 0; j < 7; j++) {
        week.push(new Date(currentDate));
        currentDate.setDate(currentDate.getDate() + 1);
      }
      weeks.push(week);
    }
    return weeks;
  })

  const calendarDateRange = computed(() => {
    if (calendarWeeks.value.length === 0) return { start: null, end: null };
    const start = calendarWeeks.value[0][0];
    const end = calendarWeeks.value[calendarWeeks.value.length - 1][6];
    return { start, end };
  })

  const isWeekInRange = (week) => {
    if (!week || !calendarDateRange.value.start || !calendarDateRange.value.end) return false;
    return getWeekNumber(week[0]) >= getWeekNumber(calendarDateRange.value.start) 
      && getWeekNumber(week[1]) <= getWeekNumber(calendarDateRange.value.end);
  }

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
    const date = new Date(week[0]);
    date.setHours(0, 0, 0, 0);
    date.setDate(date.getDate() + 3);  // 木曜日に移動（ISO 8601準拠）
    const year = date.getFullYear();
    const firstThursday = new Date(year, 0, 4);  // その年の最初の木曜日
    const weekNumber = Math.floor(1 + (date - firstThursday) / (7 * 24 * 60 * 60 * 1000));
    return `${year}-W${weekNumber.toString().padStart(2, '0')}`;
  }
  
  const getWeekFromString = (weekString) => {
    const [year, weekNumber] = weekString.split('-W').map(Number);
    const firstThursday = new Date(year, 0, 4);
    const targetThursday = new Date(firstThursday.getTime() + (weekNumber - 1) * 7 * 24 * 60 * 60 * 1000);
    const weekStart = new Date(targetThursday.getTime() - 3 * 24 * 60 * 60 * 1000);
    const weekEnd = new Date(weekStart.getTime() + 6 * 24 * 60 * 60 * 1000);
    weekStart.setHours(0, 0, 0, 0);
    weekEnd.setHours(23, 59, 59, 999);
    return [weekStart, weekEnd];
  }

  return {
    calendarWeeks,
    selectedWeek,
    selectWeek,
    calendarDateRange,
    isWeekInRange,
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