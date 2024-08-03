<template>
  <v-row
    class="weekdays"
    no-gutters
  >
    <v-col
      cols="1"
      class="week-number-header"
    >
      週
    </v-col>
    <v-col
      v-for="day in weekdays"
      :key="day.label"
      :class="['weekday', day.class]"
    >
      {{ day.label }}
    </v-col>
  </v-row>
  <transition-group
    name="week-transition"
    tag="div"
  >
    <v-row
      v-for="(week, weekIndex) in calendarWeeks"
      :key="getWeekKey(week)" 
      no-gutters
      class="week-row"
      :class="{ 
        'selected': isSelected(week), 
        'hovered': isHovered(week),
      }"
      :style="{ '--fade-delay': `${weekIndex * .05}s` }"
      @click="onSelectWeek(week)"
      @mouseenter="onHoverWeek(week)"
      @mouseleave="onLeaveWeek(week)"
    >
      <v-col
        cols="1"
        class="week-number"
      >
        {{ getWeekNumber(week[0]) }}
      </v-col>
      <v-col
        v-for="(day, dayIndex) in week"
        :key="day.toISOString()"
        :class="[
          'day',
          { 'today': isToday(day) },
          { 'saturday': isSaturday(day) },
          { 'sunday': isSunday(day) }
        ]"
      >
        <span
          v-if="shouldShowMonth(day, weekIndex, dayIndex)"
          class="month"
        >
          {{ formatShortMonth(day) }}
        </span>
        <span class="date">{{ day.getDate() }}</span>
      </v-col>
    </v-row>
  </transition-group>
</template>

<script setup>
import { ref, toRefs } from 'vue'
import { useCalendar } from '../composables/useCalendar'

const props = defineProps({
  calendarWeeks: {
    type: Array,
    required: true
  },
  onSelectWeek: {
    type: Function,
    default: () => {}
  },
  isSelected: {
    type: Function,
    default: () => {}
  },
})

const {
  calendarWeeks,
  onSelectWeek,
  isSelected
} = toRefs(props)

const { 
  shouldShowMonth,
  formatShortMonth, 
  isToday, 
  isSaturday, 
  isSunday, 
  getWeekNumber,
  getStringFromWeek
} = useCalendar()

const hoveredWeek = ref(null)

const onHoverWeek = (week) => {
  hoveredWeek.value = week
}

const onLeaveWeek = () => {
  hoveredWeek.value = null
}

const isHovered = (week) => {
  return hoveredWeek.value && week[0].getTime() === hoveredWeek.value[0].getTime()
}

const weekdays = [
  { label: '月', class: '' },
  { label: '火', class: '' },
  { label: '水', class: '' },
  { label: '木', class: '' },
  { label: '金', class: '' },
  { label: '土', class: 'saturday' },
  { label: '日', class: 'sunday' },
]

// getWeekKey is an alias for getStringFromWeek
const getWeekKey = getStringFromWeek
</script>

<style scoped>
/* 要素が追加される時（enter）と削除される時（leave） */
.week-transition-enter-active,
.week-transition-leave-active {
  height: 3em;
  transition: all 0.2s ease-out;
  transition-delay: var(--fade-delay, 0s);
} 

/* 要素が追加される直前の状態（enter-from）と、削除される直後の状態（leave-to） */
.week-transition-enter-from,
.week-transition-leave-to {
  height: 0;
  opacity: 0;
}

.week-row {
  cursor: pointer;
}

.week-row.selected {
  background-color: rgba(179, 215, 255, 0.6) !important;
}

.week-row.hovered {
  background-color: rgba(179, 215, 255, 0.3);
}

.weekdays {
  background-color: #f0f0f0;
  font-weight: bold;
}

.weekday,
.week-number-header,
.week-number,
.day {
  height: 3em;
  display: flex;
  justify-content: center;
  align-items: center;
}

.weekday {
  text-align: center;
}

.week-number-header,
.week-number {
  color: #6c757d;
  font-size: 0.8em;
}

.day {
  text-align: center;
  position: relative;
}

.day.today {
  background-color: #f3f9ff;
  border: 1px solid #a5d3ff;
  border-radius: 10px;
  font-weight: 600;
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
  font-size: 1.2em;
}

.month {
  position: absolute;
  top: 3px;
  left: 5px;
  font-size: 0.75em;
  color: #666;
}
</style>