import { computed } from 'vue'

export function useCalendar() {
  const MILLISECONDS_PER_DAY = 24 * 60 * 60 * 1000
  const WEEKDAYS = ['日', '月', '火', '水', '木', '金', '土']

  const calendarWeeks = computed(() => createWeeks(6))

  const createWeeks = (weekCount) => {
    const weeks = []
    const today = new Date()
    today.setHours(0, 0, 0, 0)

    let currentDate = new Date(today.getFullYear(), today.getMonth(), today.getDate() - 7 * (weekCount - 1))
    currentDate.setDate(currentDate.getDate() - ((currentDate.getDay() + 6) % 7))

    for (let i = 0; i < weekCount; i++) {
      const startDate = new Date(currentDate)
      weeks.push(createWeekItem(startDate, i - weekCount + 1))
      currentDate.setDate(currentDate.getDate() + 7)
    }
    return weeks
  }

  const createWeekItem = (startDate, weekOffset) => {
    const days = Array.from({ length: 7 }, (_, i) => new Date(startDate.getTime() + i * MILLISECONDS_PER_DAY))
    const endDate = new Date(startDate.getTime() + 6 * MILLISECONDS_PER_DAY)
    endDate.setHours(23, 59, 59, 999)
    return { startDate, endDate, weekOffset, days }
  }

  const getWeekOffset = (() => {
    const today = new Date()
    const currentWeekMonday = new Date(today)
    currentWeekMonday.setDate(today.getDate() - today.getDay() + (today.getDay() === 0 ? -6 : 1))
    currentWeekMonday.setHours(0, 0, 0, 0)

    return (weekStartDate) => {
      const tempDate = new Date(weekStartDate)
      tempDate.setHours(0, 0, 0, 0)
      const diffTime = tempDate.getTime() - currentWeekMonday.getTime()
      return Math.floor(diffTime / (MILLISECONDS_PER_DAY * 7))
    }
  })()

  const isWeekInRange = (week) => {
    if (!week?.startDate || !week?.endDate) return false
    
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    
    // 過去5週間前の月曜日を取得
    const minDate = new Date(today)
    minDate.setDate(today.getDate() - (5 * 7))
    const minMonday = new Date(minDate)
    minMonday.setDate(minDate.getDate() - minDate.getDay() + (minDate.getDay() === 0 ? -6 : 1))
    minMonday.setHours(0, 0, 0, 0)
  
    // 今週の日曜日を取得（現在の週の最終日）
    const currentWeekEnd = new Date(today)
    const daysUntilSunday = 7 - today.getDay()
    currentWeekEnd.setDate(today.getDate() + daysUntilSunday)
    currentWeekEnd.setHours(23, 59, 59, 999)
  
    return week.startDate >= minMonday && week.endDate <= currentWeekEnd
  }

  const getWeekNumber = (date) => {
    const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()))
    const dayNum = d.getUTCDay() || 7
    d.setUTCDate(d.getUTCDate() + 4 - dayNum)
    const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1))
    return Math.ceil((((d - yearStart) / 86400000) + 1) / 7)
  }

  const shouldShowMonth = (date, weekIndex, dayIndex) =>
    date.getDate() === 1 || (weekIndex === 0 && dayIndex === 0)

  const formatShortMonth = (date) => date.toLocaleDateString('ja-JP', { month: 'short' })

  const isToday = (() => {
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    const todayTime = today.getTime()
    return (date) => date.getTime() === todayTime
  })()

  const isSaturday = (date) => date.getDay() === 6
  const isSunday = (date) => date.getDay() === 0

  const getStringFromWeek = (week) => {
    const date = new Date(week.startDate)
    date.setDate(date.getDate() + 3)
    const year = date.getFullYear()
    const weekNumber = getWeekNumber(date)
    return `${year}-W${weekNumber.toString().padStart(2, '0')}`
  }

  const getWeekFromString = (weekString) => {
    const [year, weekNumber] = weekString.split('-W').map(Number)
    const firstThursday = new Date(year, 0, 4)
    const targetThursday = new Date(firstThursday.getTime() + (weekNumber - 1) * 7 * MILLISECONDS_PER_DAY)
    const weekStart = new Date(targetThursday.getTime() - 3 * MILLISECONDS_PER_DAY)
    weekStart.setHours(0, 0, 0, 0)
    return createWeekItem(weekStart, getWeekOffset(weekStart))
  }

  const getPreviousWeekString = (weekString) => {
    if (weekString) {
      const [year, week] = weekString.split('-W').map(Number)
      return week === 1 ? `${year - 1}-W52` : `${year}-W${(week - 1).toString().padStart(2, '0')}`
    }
    return getStringFromWeek(calendarWeeks.value[calendarWeeks.value.length - 2])
  }

  const getCurrentWeekString = () => getStringFromWeek(calendarWeeks.value[calendarWeeks.value.length - 1])

  const getWeekJpText = (relativeWeekIndex) => {
    if (relativeWeekIndex === 0) return '今週'
    if (relativeWeekIndex === -1) return '先週'
    if (relativeWeekIndex === 1) return '来週'
    return relativeWeekIndex < 0 ? `${Math.abs(relativeWeekIndex)}週前` : `${relativeWeekIndex}週後`
  }

  const formatFullDateTimeJp = (date) => {
    if (!(date instanceof Date) || isNaN(date)) return ''
    const year = date.getFullYear()
    const month = date.getMonth() + 1
    const day = date.getDate()
    const weekday = WEEKDAYS[date.getDay()]
    const hour = date.getHours().toString().padStart(2, '0')
    const minute = date.getMinutes().toString().padStart(2, '0')
    return `${year}/${month}/${day} (${weekday}) ${hour}:${minute}`
  }

  const formatDateJp = (date) => {
    const year = date.getFullYear()
    const month = (date.getMonth() + 1).toString().padStart(2, '0')
    const day = date.getDate().toString().padStart(2, '0')
    return `${year}/${month}/${day}`
  }

  const formatDateTimeJp = (date) => {
    const formattedDate = formatDateJp(date)
    const formattedTime = date.toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' })
    return `${formattedDate} ${formattedTime}`
  }

  const formatDateRange = (week) => {
    const options = { year: 'numeric', month: 'long', day: 'numeric' }
    return `${week.startDate.toLocaleDateString('ja-JP', options)} - ${week.endDate.toLocaleDateString('ja-JP', options)}`
  }

  return {
    calendarWeeks,
    createWeeks,
    isWeekInRange,
    getWeekNumber,
    formatShortMonth,
    isToday,
    isSaturday,
    isSunday,
    shouldShowMonth,
    getStringFromWeek,
    getWeekFromString,
    getPreviousWeekString,
    getCurrentWeekString,
    getWeekJpText,
    formatDateJp,
    formatDateTimeJp,
    formatFullDateTimeJp,
    formatDateRange
  }
}