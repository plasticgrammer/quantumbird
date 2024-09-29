<template>
  <v-row
    class="weekdays"
    no-gutters
  >
    <v-col class="week-number-header">
      週
    </v-col>
    <v-col
      v-for="day in weekdays"
      :key="day.label"
      :class="['weekday-header', day.class]"
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
      <v-col class="week-number">
        {{ getWeekJpText(week.weekOffset) }}
      </v-col>
      <v-col
        v-for="(day, dayIndex) in week.days"
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
          :style="{ fontSize: monthFontSize }"
        >
          {{ formatShortMonth(day) }}
        </span>
        <span class="date">{{ day.getDate() }}</span>
      </v-col>
    </v-row>
  </transition-group>
</template>

<script setup>
import { ref, toRefs, onMounted, onUnmounted, computed } from 'vue'
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
  getStringFromWeek,
  getWeekJpText
} = useCalendar()

const hoveredWeek = ref(null)

const onHoverWeek = (week) => {
  hoveredWeek.value = week
}

const onLeaveWeek = () => {
  hoveredWeek.value = null
}

const isHovered = (week) => {
  return hoveredWeek.value && week.weekOffset === hoveredWeek.value.weekOffset
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

const containerWidth = ref(0)
const monthFontSize = computed(() => {
  return containerWidth.value >= 600 ? '1em' : '0.75em'
})

const updateContainerWidth = () => {
  const container = document.querySelector('.week-row')
  if (container) {
    containerWidth.value = container.offsetWidth
  }
}

onMounted(() => {
  updateContainerWidth()
  window.addEventListener('resize', updateContainerWidth)
})

onUnmounted(() => {
  window.removeEventListener('resize', updateContainerWidth)
})
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

.weekday-header,
.week-number-header {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 2.5em;
}

.weekday,
.week-number,
.day {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 3.3em;
}

.week-number-header,
.week-number {
  font-weight: bold;
  background-color: #e0e0e0;
  border-right: 1px solid #ccc;
  font-size: 1.1em;
  max-width: 80px;
  min-width: 60px;
}

.week-number {
  text-orientation: upright;
  white-space: nowrap;
}

.week-row:hover .week-number {
  background-color: #d0d0d0;
}

.week-row.selected .week-number {
  background-color: #b3d7ff;
}

.weekday {
  text-align: center;
}

.day {
  text-align: center;
  position: relative;
  margin-top: 2px;
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
  color: #0000ff;
}

.day.sunday {
  color: #ff0000;
}

.date {
  font-size: 1.2em;
}

.month {
  position: absolute;
  top: 2px;
  left: 6px;
  color: navy;
}
</style>