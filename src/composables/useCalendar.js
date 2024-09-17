import { computed } from 'vue'

export function useCalendar() {
  const calendarWeeks = computed(() => createWeeks(6))

  const createWeeks = (weekCount) => {
    const weeks = []
    const today = new Date()

    let currentDate = new Date(today.getFullYear(), today.getMonth(), today.getDate() - 7 * (weekCount - 1))

    // 最初の月曜日まで移動
    while (currentDate.getDay() !== 1) {
      currentDate.setDate(currentDate.getDate() - 1)
    }

    for (let i = 0; i < weekCount; i++) {
      const days = []
      const startDate = new Date(currentDate)
      for (let j = 0; j < 7; j++) {
        days.push(new Date(currentDate))
        currentDate.setDate(currentDate.getDate() + 1)
      }
      weeks.push(createWeekItem(startDate, i - weekCount + 1))
    }
    return weeks
  }

  const createWeekItem = (startDate, weekOffset) => {
    const days = []
    const currentDate = new Date(startDate)
    for (let j = 0; j < 7; j++) {
      days.push(new Date(currentDate))
      currentDate.setDate(currentDate.getDate() + 1)
    }
    const endDate = new Date(startDate.getTime() + 6 * 24 * 60 * 60 * 1000)
    endDate.setHours(23, 59, 59, 999)
    return {
      startDate,
      endDate,
      weekOffset,
      days
    }
  }

  function getWeekOffset(weekStartDate) {
    // 現在の日付を取得
    const today = new Date()

    // 現在の週の月曜日を取得
    const currentWeekMonday = new Date(today)
    currentWeekMonday.setDate(today.getDate() - today.getDay() + (today.getDay() === 0 ? -6 : 1))
    currentWeekMonday.setHours(0, 0, 0, 0)

    // 引数で渡された週の月曜日の時間をリセット
    weekStartDate.setHours(0, 0, 0, 0)

    // 週の差分を計算
    const diffTime = weekStartDate.getTime() - currentWeekMonday.getTime()
    const diffDays = Math.round(diffTime / (1000 * 60 * 60 * 24))
    const weekOffset = Math.floor(diffDays / 7)

    return weekOffset
  }

  const isWeekInRange = (week) => {
    if (!week) return false
    const start = calendarWeeks.value[0].startDate
    const end = calendarWeeks.value[calendarWeeks.value.length - 1].endDate
    if (!start || !end) return false
    return week.startDate.getTime() >= start.getTime()
      && week.endDate.getTime() <= end.getTime()
  }

  const getWeekNumber = (date) => {
    const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()))
    const dayNum = d.getUTCDay() || 7
    d.setUTCDate(d.getUTCDate() + 4 - dayNum)
    const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1))
    return Math.ceil((((d - yearStart) / 86400000) + 1) / 7)
  }

  const shouldShowMonth = (date, weekIndex, dayIndex) => {
    if (date.getDate() === 1) return true // 毎月1日
    if (weekIndex === 0 && dayIndex === 0) return true // カレンダーの最初の日
    return false
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
    const date = new Date(week.startDate)
    date.setHours(0, 0, 0, 0)
    date.setDate(date.getDate() + 3) // 木曜日に移動（ISO 8601準拠）
    const year = date.getFullYear()
    const firstThursday = new Date(year, 0, 4) // その年の最初の木曜日
    const weekNumber = Math.floor(1 + (date - firstThursday) / (7 * 24 * 60 * 60 * 1000))
    return `${year}-W${weekNumber.toString().padStart(2, '0')}`
  }

  const getWeekFromString = (weekString) => {
    const [year, weekNumber] = weekString.split('-W').map(Number)
    const firstThursday = new Date(year, 0, 4)
    const targetThursday = new Date(firstThursday.getTime() + (weekNumber - 1) * 7 * 24 * 60 * 60 * 1000)
    const weekStart = new Date(targetThursday.getTime() - 3 * 24 * 60 * 60 * 1000)
    weekStart.setHours(0, 0, 0, 0)
    return createWeekItem(weekStart, getWeekOffset(weekStart))
  }

  const getPreviousWeekString = (weekString) => {
    if (weekString) {
      const [year, week] = weekString.split('-W').map(Number)
      if (week === 1) {
        return `${year - 1}-W52`
      }
      return `${year}-W${(week - 1).toString().padStart(2, '0')}`
    } else {
      return getStringFromWeek(calendarWeeks.value.slice(-2)[0])
    }
  }

  const getCurrentWeekString = () => {
    return getStringFromWeek(calendarWeeks.value.slice(-1)[0])
  }

  const getWeekJpText = (relativeWeekIndex) => {
    if (relativeWeekIndex === 0) return '今週'
    if (relativeWeekIndex === -1) return '先週'
    if (relativeWeekIndex === 1) return '来週'
    if (relativeWeekIndex < 0) return `${Math.abs(relativeWeekIndex)}週前`
    return `${relativeWeekIndex}週後`
  }

  const formatFullDateTimeJp = (date) => {
    if (!(date instanceof Date)) {
      return ''
    }

    const weekdays = ['日', '月', '火', '水', '木', '金', '土']
    const year = date.getFullYear()
    const month = date.getMonth() + 1 // getMonth() returns 0-11
    const day = date.getDate()
    const weekday = weekdays[date.getDay()]
    const hour = date.getHours().toString().padStart(2, '0')
    const minute = date.getMinutes().toString().padStart(2, '0')

    return `${year}/${month}/${day} (${weekday})  ${hour}:${minute}`
  }

  const formatDateJp = (date) => {
    const year = date.getFullYear()
    const month = ('0' + (date.getMonth() + 1)).slice(-2)
    const day = ('0' + date.getDate()).slice(-2)
    return `${year}/${month}/${day}`
  }

  const formatDateTimeJp = (date) => {
    const timeOptions = { hour: '2-digit', minute: '2-digit' }
    const formattedTime = date.toLocaleTimeString('ja-JP', timeOptions)

    return `${formatDateJp(date)} ${formattedTime}`
  }

  const formatDateRange = (week) => {
    const start = week.startDate
    const end = week.endDate
    const options = { year: 'numeric', month: 'long', day: 'numeric' }
    return `${start.toLocaleDateString('ja-JP', options)} - ${end.toLocaleDateString('ja-JP', options)}`
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