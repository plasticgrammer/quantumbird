<template>
  <BaseWidget
    widget-id="calendar"
    title="報告状況"
    icon="mdi-calendar-multiple-check"
  >
    <v-row>
      <v-col cols="12" :md="expanded ? 9 : 12">
        <v-card max-width="560" class="mx-auto calendar-card">
          <v-container class="pa-0 position-relative">
            <div v-for="(week, index) in calendarWeeks" :key="index" :class="{ 'd-none': index !== weekIndex }">
              <Calendar :calendar-weeks="[week]" />
            </div>
            <v-btn
              v-if="weekIndex > 0"
              class="calendar-nav-btn calendar-nav-btn-left"
              icon="mdi-arrow-left-thick"
              size="small"
              fab
              aria-label="前の週へ"
              @click="handleWeekChange(-1)"
            ></v-btn>
            <v-btn
              v-if="weekIndex < calendarWeeks.length - 1"
              class="calendar-nav-btn calendar-nav-btn-right"
              icon="mdi-arrow-right-thick"
              size="small"
              fab
              aria-label="次の週へ"
              @click="handleWeekChange(1)"
            ></v-btn>
          </v-container>
        </v-card>
        <v-badge 
          class="mt-6"
          :color="statusCounts['pending'] ? 'info' : 'transparent'"
          :content="statusCounts['pending'] || ''"
        >
          <v-btn 
            color="black" variant="outlined"
            :to="{ name: 'WeeklyReview', params: { weekString } }"
            aria-label="週次報告レビューへ移動"
          >
            <v-icon class="mr-1" small left aria-hidden="true">
              mdi-calendar-multiple-check
            </v-icon>
            週次報告レビュー
          </v-btn>
        </v-badge>
      </v-col>
      <v-col 
        cols="12" 
        :md="expanded ? 3 : 12" 
        :class="[
          'd-flex',
          expanded ? 'flex-sm-column' : 'flex-wrap',
          'align-start',
          'pt-2'
        ]"
      >
        <span 
          v-for="status in filteredStatusOptions" 
          :key="status.value"
          :class="{ 'status-chip-wrapper': !expanded }"
        >
          <v-chip
            v-if="statusCounts[status.value] > 0"
            v-tooltip:end="statusMembers[status.value]?.join(', ') || ''"
            class="ma-1"
            :value="status.value"
            :color="status.color"
            label
          >
            {{ status.text }}: {{ statusCounts[status.value] }}
          </v-chip>
        </span>
      </v-col>
    </v-row>
  </BaseWidget>
</template>

<script setup>
import { useWidgets } from '../../composables/useWidgets'
import Calendar from '../Calendar.vue'
import BaseWidget from './BaseWidget.vue'

const props = defineProps({
  calendarWeeks: { type: Array, required: true },
  weekIndex: { type: Number, required: true },
  statusCounts: { type: Object, required: true },
  statusMembers: { type: Object, required: true },
  filteredStatusOptions: { type: Array, required: true },
  weekString: { type: String, required: true }
})

const emit = defineEmits(['update:weekIndex'])
const { isExpanded } = useWidgets()
const expanded = isExpanded('calendar')

const handleWeekChange = (delta) => {
  const newIndex = delta > 0
    ? Math.min(props.calendarWeeks.length - 1, props.weekIndex + 1)
    : Math.max(0, props.weekIndex - 1)
  emit('update:weekIndex', newIndex)
}
</script>

<style scoped>
.calendar-small :deep(.v-date-picker-month) {
  height: 240px;
}

.calendar-small :deep(.v-date-picker-month__day) {
  width: 28px;
  height: 28px;
  font-size: 0.9rem;
}

.calendar-small :deep(.v-date-picker-controls) {
  display: none;
}

.calendar-card {
  overflow: visible !important;
  max-width: v-bind(expanded ? '560px' : '100%');
  margin: 0 auto;
}

.position-relative {
  position: relative;
}

.calendar-nav-btn {
  opacity: 0.6;
  position: absolute;
  bottom: 6px;
}

.calendar-nav-btn-left {
  left: -30px;
}

.calendar-nav-btn-right {
  right: -30px;
}

.widget :deep(.v-card-title) {
  user-select: none;
}

.status-chip-wrapper {
  display: inline-block;
}
</style>