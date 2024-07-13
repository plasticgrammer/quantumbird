<template>
  <v-container 
    class="week-selector"
    @mouseenter="startHoverTimer"
    @mouseleave="handleMouseLeave"
  >
    <v-row align="center" justify="space-between" class="mb-1">
      <v-col class="py-4">
        <h3>
          <v-icon size="x-large" class="mr-1">mdi-bird</v-icon>
          {{ selectedWeekRange }}
        </h3>
      </v-col>
    </v-row>
    <v-card elevation="4">
      <v-card-text class="pa-0">
        <v-row class="weekdays" no-gutters>
          <v-col cols="1" class="week-number-header">週</v-col>
          <v-col v-for="day in weekdays" :key="day.label" :class="['weekday', day.class]">
            {{ day.label }}
          </v-col>
        </v-row>
        <transition-group name="week-transition" tag="div">
          <v-row v-for="(week, weekIndex) in visibleWeeks" :key="getWeekKey(week)" 
            no-gutters
            class="week-row"
            :class="{ 
              'selected': isSelected(week), 
              'hovered': isHovered(week),
            }"
            :style="{ '--fade-delay': `${weekIndex * .10}s` }"
            @click="selectWeek(week)"
            @mouseenter="setHoverWeek(week)"
            @mouseleave="clearHoverWeek"
          >
            <v-col cols="1" class="week-number">{{ getWeekNumber(week[0]) }}</v-col>
            <v-col v-for="(day, dayIndex) in week" :key="day.toISOString()"
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
            </v-col>
          </v-row>
        </transition-group>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { useCalendar } from '../composables/useCalendar'

export default {
  name: 'WeekSelector',
  props: {
    selectedWeek: {
      type: Array,
      default: () => null
    },
  },
  emits: ['select-week'],
  setup(props, { emit }) {
    const { 
      formatShortMonth, 
      isToday, 
      isSaturday, 
      isSunday, 
      shouldShowMonth,
      getWeekNumber,
      getStringFromWeek,
      calendarWeeks
    } = useCalendar()

    const internalSelectedWeek = ref(props.selectedWeek)
    const hoveredWeek = ref(null);
    const showAllWeeks = ref(false);
    let hoverTimer = null;

    const visibleWeeks = computed(() => {
      if (!internalSelectedWeek.value || showAllWeeks.value) return calendarWeeks.value;
      return calendarWeeks.value.filter(week => {
        const weekStart = week[0];
        return weekStart >= internalSelectedWeek.value[0] && weekStart <= internalSelectedWeek.value[1];
      });
    });

    const weekdays = [
      { label: '月', class: '' },
      { label: '火', class: '' },
      { label: '水', class: '' },
      { label: '木', class: '' },
      { label: '金', class: '' },
      { label: '土', class: 'saturday' },
      { label: '日', class: 'sunday' },
    ]

    const selectWeek = (week) => {
      internalSelectedWeek.value = [week[0], new Date(week[0].getTime() + 6 * 24 * 60 * 60 * 1000)];
      showAllWeeks.value = false;
      emit('select-week', internalSelectedWeek.value);
    }

    const isSelected = (week) => {
      return internalSelectedWeek.value && week[0].getTime() === internalSelectedWeek.value[0].getTime();
    }

    const setHoverWeek = (week) => {
      hoveredWeek.value = week;
    }

    const clearHoverWeek = () => {
      hoveredWeek.value = null;
    }

    const isHovered = (week) => {
      return hoveredWeek.value && week[0].getTime() === hoveredWeek.value[0].getTime();
    }

    const formatDateRange = (week) => {
      if (!week || week.length < 2) return '週の選択';
      const start = week[0];
      const end = week[1];
      const options = { year: 'numeric', month: 'long', day: 'numeric' };
      return `${start.toLocaleDateString('ja-JP', options)} - ${end.toLocaleDateString('ja-JP', options)}`;
    }

    const selectedWeekRange = computed(() => {
      return internalSelectedWeek.value ? formatDateRange(internalSelectedWeek.value) : '週の選択';
    });

    const startHoverTimer = () => {
      if (internalSelectedWeek.value && !showAllWeeks.value) {
        hoverTimer = setTimeout(() => {
          showAllWeeks.value = true;
        }, 300);
      }
    }

    const handleMouseLeave = () => {
      clearTimeout(hoverTimer);
      showAllWeeks.value = false;
    }

    watch(() => props.selectedWeek, (newValue) => {
      internalSelectedWeek.value = newValue;
      showAllWeeks.value = false;
    });
    
    return {
      visibleWeeks,
      weekdays,
      internalSelectedWeek,
      selectWeek,
      isSelected,
      setHoverWeek,
      clearHoverWeek,
      isHovered,
      getWeekNumber,
      formatShortMonth,
      isToday,
      isSaturday,
      isSunday,
      shouldShowMonth,
      selectedWeekRange,
      getWeekKey: getStringFromWeek,
      startHoverTimer,
      handleMouseLeave
    }
  }
}
</script>

<style scoped>
.week-selector {
  max-width: 800px;
}

/* 要素が追加される時（enter）と削除される時（leave） */
.week-transition-enter-active,
.week-transition-leave-active {
  height: 3em;
  transition: all 0.4s ease-out;
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

.week-row.selected,
.week-row.hovered {
  background-color: rgba(179, 215, 255, 0.5);
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