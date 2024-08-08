<template>
  <v-container class="week-selector">
    <v-row dense class="pb-3">
      <v-col>
        <h3>
          <v-icon
            :icon="icon"
            size="large"
            class="mr-1"
          />
          {{ functionName }}［{{ selectedWeekRange }}］
        </h3>
      </v-col>
    </v-row>
    <v-card 
      class="d-print-none"
      :class="{ 'hover-effect': isHovering, 'leave-effect': !isHovering, 'show-all-weeks': showAllWeeks }"
      @mouseenter="handleMouseEnter"
      @mouseleave="handleMouseLeave"
    >
      <v-card-text class="pa-0">
        <Calendar
          :calendar-weeks="visibleWeeks"
          :on-select-week="handleSelectWeek"
          :is-selected="isSelected"
        />
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useCalendar } from '../composables/useCalendar'
import Calendar from './Calendar.vue'

const props = defineProps({
  functionName: {
    type: String,
    required: true
  },
  selectedWeek: {
    type: Object,
    default: () => null
  },
  icon: {
    type: String,
    default: 'mdi-bird'
  }
})

const emit = defineEmits(['select-week', 'reset'])

const {
  calendarWeeks,
  getWeekJpText
} = useCalendar()

const internalSelectedWeek = ref(props.selectedWeek)
const isHovering = ref(false)
const showAllWeeks = ref(false)

const visibleWeeks = computed(() => {
  if (!internalSelectedWeek.value || showAllWeeks.value) return calendarWeeks.value
  return calendarWeeks.value.filter(week => {
    return internalSelectedWeek.value.weekOffset == week.weekOffset 
  })
})

const handleSelectWeek = (week) => {
  if (internalSelectedWeek.value && !showAllWeeks.value) {
    showAllWeeks.value = true
    emit('reset')
  } else {
    internalSelectedWeek.value = week
    setTimeout(() => {
      showAllWeeks.value = false
      emit('select-week', internalSelectedWeek.value)
    }, 500)
  }
}

const isSelected = (week) => {
  return internalSelectedWeek.value && week.weekOffset === internalSelectedWeek.value.weekOffset
}

const selectedWeekRange = computed(() => {
  return internalSelectedWeek.value ? getWeekJpText(internalSelectedWeek.value.weekOffset) : '週の選択'
})

const handleMouseEnter = () => {
  isHovering.value = true
}

const handleMouseLeave = () => {
  isHovering.value = false
}

watch(() => props.selectedWeek, (newValue) => {
  internalSelectedWeek.value = newValue
  showAllWeeks.value = false
})
</script>

<style scoped>
.week-selector {
  padding: 0;
}

.hover-effect {
  transition: all 0.3s ease;
  transform: scale(1.02);
}

.leave-effect {
  transition: all 0.3s ease;
  transform: scale(1);
}

.show-all-weeks {
  transition: all 0.3s ease;
  transform: scale(1.02);
}
</style>