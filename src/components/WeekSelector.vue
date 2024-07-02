<template>
  <div class="week-selector">
    <div class="week-selector-header">
      <h3>週の選択</h3>
      <div v-if="selectedWeek" class="selected-week-range">
        {{ formatDateRange(selectedWeek.start, selectedWeek.end) }}
      </div>
    </div>
    <div class="calendar">
      <div class="weekdays">
        <div class="week-number-header">週</div>
        <div v-for="day in weekdays" :key="day.label" :class="day.class">{{ day.label }}</div>
      </div>
      <div class="days">
        <template v-for="(week, weekIndex) in calendarWeeks" :key="weekIndex">
          <div class="week-number">
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
    <button v-if="selectedWeek" @click="resetSelection" class="reset-button">選択をリセット</button>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useCalendar } from '../composables/useCalendar'

export default {
  name: 'WeekSelector',
  emits: ['select-week'],
  setup(props, { emit }) {
    const { 
      calendarWeeks,
      weekdays,
      selectedWeek,
      selectWeek,
      getWeekNumber,
      formatShortMonth,
      isToday,
      isSaturday,
      isSunday,
      shouldShowMonth
    } = useCalendar()

    const hoveredWeek = ref(null)

    const selectDate = (date) => {
      const weekStart = new Date(date)
      weekStart.setDate(weekStart.getDate() - weekStart.getDay() + 1)
      const weekEnd = new Date(weekStart)
      weekEnd.setDate(weekEnd.getDate() + 6)
      
      const week = { start: weekStart, end: weekEnd }
      selectWeek(week)
      emit('select-week', week)
    }

    const isSelected = (date) => {
      if (!selectedWeek.value) return false
      return date >= selectedWeek.value.start && date <= selectedWeek.value.end
    }

    const setHoverWeek = (date) => {
      const weekStart = new Date(date)
      weekStart.setDate(weekStart.getDate() - weekStart.getDay() + 1)
      const weekEnd = new Date(weekStart)
      weekEnd.setDate(weekEnd.getDate() + 6)
      hoveredWeek.value = { start: weekStart, end: weekEnd }
    }

    const clearHoverWeek = () => {
      hoveredWeek.value = null
    }

    const isHovered = (date) => {
      if (!hoveredWeek.value) return false
      return date >= hoveredWeek.value.start && date <= hoveredWeek.value.end
    }

    const resetSelection = () => {
      selectWeek(null)
      emit('select-week', null)
    }

    const formatDateRange = (start, end) => {
      const options = { year: 'numeric', month: 'long', day: 'numeric' }
      return `${start.toLocaleDateString('ja-JP', options)} - ${end.toLocaleDateString('ja-JP', options)}`
    }

    return {
      calendarWeeks,
      weekdays,
      selectedWeek,
      selectDate,
      isSelected,
      isHovered,
      setHoverWeek,
      clearHoverWeek,
      isToday,
      isSaturday,
      isSunday,
      getWeekNumber,
      formatShortMonth,
      shouldShowMonth,
      resetSelection,
      formatDateRange
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
  margin-bottom: 10px;
}

.week-selector h3 {
  margin: 0;
}

.selected-week-range {
  font-size: 0.9em;
  color: #666;
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
  background-color: #f8f9fa;
  color: #6c757d;
  font-size: 0.8em;
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

.reset-button {
  margin-top: 10px;
  padding: 5px 10px;
  background-color: #f0f0f0;
  border: 1px solid #ccc;
  border-radius: 4px;
  cursor: pointer;
}

.reset-button:hover {
  background-color: #e0e0e0;
}

@media (max-width: 768px) {
  .week-selector-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .selected-week-range {
    margin-top: 5px;
  }
}
</style>