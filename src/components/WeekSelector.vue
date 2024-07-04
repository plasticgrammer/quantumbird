<template>
  <div class="week-selector">
    <div class="week-selector-header">
      <h3>{{ selectedWeekRange }}</h3>
      <button v-if="isLocked" @click="resetSelection" class="reset-button">
        選択をリセット
      </button>
    </div>
    <div class="calendar">
      <div class="weekdays">
        <div class="week-number-header">週</div>
        <div v-for="day in weekdays" :key="day.label" :class="day.class">{{ day.label }}</div>
      </div>
      <transition-group name="week-fade" tag="div" class="weeks">
        <div 
          v-for="(week, weekIndex) in visibleWeeks" 
          :key="getWeekKey(week)" 
          class="week-row"
          :class="{ 
            'selected': isSelected(week), 
            'hovered': isHovered(week) 
          }"
          @click="selectWeek(week)"
          @mouseenter="setHoverWeek(week)"
          @mouseleave="clearHoverWeek"
        >
          <div class="week-number">{{ getWeekNumber(week[0]) }}</div>
          <div
            v-for="(day, dayIndex) in week"
            :key="day.toISOString()"
            :class="[
              'day',
              { 'today': isToday(day) },
              { 'saturday': isSaturday(day) },
              { 'sunday': isSunday(day) }
            ]"
          >
            <span v-if="shouldShowMonth(day, weekIndex, dayIndex)" class="month">
              {{ formatShortMonth(day) }}
            </span>
            <span class="date">{{ day.getDate() }}</span>
          </div>
        </div>
      </transition-group>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { useCalendar } from '../composables/useCalendar'

export default {
  name: 'WeekSelector',
  props: {
    isLocked: {
      type: Boolean,
      default: false
    }
  },
  emits: ['select-week', 'reset'],
  setup(props, { emit }) {
    const { formatShortMonth, isToday, isSaturday, isSunday } = useCalendar()

    const selectedWeek = ref(null)
    const hoveredWeek = ref(null)
    const isLocked = ref(false)

    const weekdays = [
      { label: '日', class: 'sunday' },
      { label: '月', class: '' },
      { label: '火', class: '' },
      { label: '水', class: '' },
      { label: '木', class: '' },
      { label: '金', class: '' },
      { label: '土', class: 'saturday' }
    ]

    const calendarWeeks = computed(() => {
      const weeks = []
      const today = new Date()
      let currentDate = new Date(today)

      // 今日の日付を含む週の日曜日まで戻る
      while (currentDate.getDay() !== 0) {
        currentDate.setDate(currentDate.getDate() - 1)
      }

      // さらに3週間前に戻る
      currentDate.setDate(currentDate.getDate() - 21)

      for (let i = 0; i < 4; i++) {
        const week = []
        for (let j = 0; j < 7; j++) {
          week.push(new Date(currentDate))
          currentDate.setDate(currentDate.getDate() + 1)
        }
        weeks.push(week)
      }
      return weeks
    })

    const visibleWeeks = computed(() => {
      if (!selectedWeek.value) return calendarWeeks.value
      return calendarWeeks.value.filter(week => 
        week[0].getTime() === selectedWeek.value[0].getTime()
      )
    })

    const getWeekKey = (week) => week[0].toISOString().split('T')[0]

    // selectedWeek の変更を監視し、isLocked を更新
    watch(selectedWeek, (newValue) => {
      isLocked.value = newValue !== null && visibleWeeks.value.length === 1
    })

    const selectWeek = (week) => {
      if (props.isLocked) return
      selectedWeek.value = selectedWeek.value && 
        selectedWeek.value[0].getTime() === week[0].getTime() ? null : week
      emit('select-week', selectedWeek.value)
    }

    const resetSelection = () => {
      selectedWeek.value = null
      emit('reset')
    }

    const isSelected = (week) => {
      return !isLocked.value && selectedWeek.value && week[0].getTime() === selectedWeek.value[0].getTime()
    }

    const setHoverWeek = (week) => {
      hoveredWeek.value = week
    }

    const clearHoverWeek = () => {
      hoveredWeek.value = null
    }

    const isHovered = (week) => {
      return hoveredWeek.value && week[0].getTime() === hoveredWeek.value[0].getTime()
    }

    const formatDateRange = (week) => {
      if (!week) return ''
      const start = week[0]
      const end = week[6]
      const options = { year: 'numeric', month: 'long', day: 'numeric' }
      return `${start.toLocaleDateString('ja-JP', options)} - ${end.toLocaleDateString('ja-JP', options)}`
    }

    const selectedWeekRange = computed(() => {
      return selectedWeek.value
        ? formatDateRange(selectedWeek.value)
        : '週の選択'
    })

    const shouldShowMonth = (date, weekIndex, dayIndex) => {
      return date.getDate() === 1 || (weekIndex === 0 && dayIndex === 0)
    }

    const getWeekNumber = (date) => {
      const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
      const dayNum = d.getUTCDay() || 7;
      d.setUTCDate(d.getUTCDate() + 4 - dayNum);
      const yearStart = new Date(Date.UTC(d.getUTCFullYear(),0,1));
      return Math.ceil((((d - yearStart) / 86400000) + 1)/7);
    }

    return {
      visibleWeeks,
      weekdays,
      selectedWeek,
      selectWeek,
      isSelected,
      setHoverWeek,
      clearHoverWeek,
      isHovered,
      resetSelection,
      getWeekNumber,
      formatShortMonth,
      isToday,
      isSaturday,
      isSunday,
      shouldShowMonth,
      selectedWeekRange,
      getWeekKey
    }
  }
}
</script>

<style scoped>
.week-selector {
  margin-bottom: 20px;
}

.week-selector-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.week-selector h3 {
  margin: 5px 0;
  font-size: 1.2em;
  color: #333;
}

.reset-button {
  background-color: #f0f0f0;
  border: 1px solid #ccc;
  border-radius: 4px;
  padding: 5px 10px;
  font-size: 0.9em;
  cursor: pointer;
  transition: background-color 0.2s;
}

.reset-button:hover {
  background-color: #e0e0e0;
}

.calendar {
  border: 1px solid #ddd;
  border-radius: 5px;
  overflow: hidden;
}

.weekdays {
  display: grid;
  grid-template-columns: 40px repeat(7, 1fr);
  background-color: #f0f0f0;
  font-weight: bold;
}

.weekdays > div {
  padding: 10px;
  text-align: center;
}

.week-number-header,
.week-number {
  background-color: #f8f9fa;
  color: #6c757d;
  font-size: 0.8em;
  display: flex;
  justify-content: center;
  align-items: center;
}

.weeks {
  display: flex;
  flex-direction: column;
}

.week-row {
  display: grid;
  grid-template-columns: 40px repeat(7, 1fr);
  transition: all 0.3s ease;
  cursor: pointer;
}

.week-row.selected,
.week-row.hovered {
  background-color: rgba(179, 215, 255, 0.5);
}

.week-row.selected .week-number,
.week-row.hovered .week-number {
  background-color: transparent;
}

.day {
  padding: 10px;
  text-align: center;
  position: relative;
}

.day.today {
  background: linear-gradient(135deg, #f3f9ff 0%, #e1f1ff 100%);
  border: 1px solid #a5d3ff;
  border-radius: 8px;
  font-weight: bold;
  color: #3b82c4;
  overflow: hidden;
}

.day.saturday {
  color: #0000FF;
}

.day.sunday {
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

.week-fade-enter-active,
.week-fade-leave-active {
  transition: all 0.5s ease-out;
}

.week-fade-enter-from,
.week-fade-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}
</style>