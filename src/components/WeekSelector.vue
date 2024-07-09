<template>
  <v-container class="week-selector">
    <v-row align="center" justify="space-between" class="mb-1">
      <v-col>
        <h3>{{ selectedWeekRange }}</h3>
      </v-col>
      <v-col class="text-right">
        <v-btn
          v-if="isLocked"
          @click="resetSelection"
          color="secondary"
          small
        >
          選択をリセット
        </v-btn>
      </v-col>
    </v-row>
    <v-card>
      <v-card-text class="pa-0">
        <v-row class="weekdays" no-gutters>
          <v-col cols="1" class="week-number-header">週</v-col>
          <v-col v-for="day in weekdays" :key="day.label" :class="['weekday', day.class]">
            {{ day.label }}
          </v-col>
        </v-row>
        <v-row v-for="(week, weekIndex) in visibleWeeks" :key="getWeekKey(week)" no-gutters
          class="week-row"
          :class="{ 
            'selected': isSelected(week), 
            'hovered': isHovered(week) 
          }"
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
    isLocked: {
      type: Boolean,
      default: false
    }
  },
  emits: ['select-week', 'reset'],
  setup(props, { emit }) {
    const { 
      formatShortMonth, 
      isToday, 
      isSaturday, 
      isSunday, 
      shouldShowMonth,
      getWeekNumber,
      calendarWeeks
    } = useCalendar()

    const internalSelectedWeek = ref(props.selectedWeek)

    const visibleWeeks = computed(() => {
      console.log('Computing visibleWeeks, internalSelectedWeek:', internalSelectedWeek.value);
      if (!internalSelectedWeek.value) return calendarWeeks.value;
      return calendarWeeks.value.filter(week => {
        if (!Array.isArray(week) || week.length === 0 || !(week[0] instanceof Date)) {
          console.error('Invalid week in calendarWeeks:', week);
          return false;
        }
        const weekStart = week[0];
        return weekStart >= internalSelectedWeek.value[0] && weekStart <= internalSelectedWeek.value[1];
      });
    });

    const weekdays = [
      { label: '日', class: 'sunday' },
      { label: '月', class: '' },
      { label: '火', class: '' },
      { label: '水', class: '' },
      { label: '木', class: '' },
      { label: '金', class: '' },
      { label: '土', class: 'saturday' }
    ]

    watch(() => props.selectedWeek, (newSelectedWeek) => {
      console.log('props.selectedWeek changed:', newSelectedWeek);
      internalSelectedWeek.value = newSelectedWeek;
    }, { immediate: true });

    const selectWeek = (week) => {
      if (props.isLocked) return;
      const newSelectedWeek = internalSelectedWeek.value && 
        internalSelectedWeek.value[0].getTime() === week[0].getTime() ? null : [week[0], new Date(week[0].getTime() + 6 * 24 * 60 * 60 * 1000)];
      internalSelectedWeek.value = newSelectedWeek;
      emit('select-week', newSelectedWeek);
    };

    const resetSelection = () => {
      internalSelectedWeek.value = null;
      emit('reset');
    }

    const isSelected = (week) => {
      return internalSelectedWeek.value && week[0].getTime() === internalSelectedWeek.value[0].getTime();
    }

    const hoveredWeek = ref(null);

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

    const getWeekKey = (week) => {
      if (!Array.isArray(week) || week.length === 0) {
        console.error('Invalid week in getWeekKey:', week);
        return 'invalid-week';
      }
      if (!(week[0] instanceof Date)) {
        console.error('First element of week is not a Date:', week[0]);
        return 'invalid-date';
      }
      try {
        return week[0].toISOString().split('T')[0];
      } catch (error) {
        console.error('Error in getWeekKey:', error);
        return 'error-week';
      }
    }

    return {
      visibleWeeks,
      weekdays,
      internalSelectedWeek,
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

.week-row {
  transition: all 0.3s ease;
  cursor: pointer;
}

.week-row.selected,
.week-row.hovered {
  background-color: rgba(179, 215, 255, 0.5);
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
  top: 2px;
  left: 4px;
  font-size: 0.7em;
  color: #666;
}
</style>