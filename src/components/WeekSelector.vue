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
          {{ selectedWeekRange }}
        </h3>
      </v-col>
    </v-row>
    <v-card 
      elevation="4"
      :class="{ 'hover-effect': isHovering, 'leave-effect': !isHovering, 'show-all-weeks': showAllWeeks }"
      @mouseenter="handleMouseEnter"
      @mouseleave="handleMouseLeave"
    >
      <Calendar
        :calendar-weeks="visibleWeeks"
        :on-select-week="handleSelectWeek"
        :is-selected="isSelected"
      />
    </v-card>
  </v-container>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useCalendar } from '../composables/useCalendar'
import Calendar from './Calendar.vue'

const props = defineProps({
  selectedWeek: {
    type: Array,
    default: () => null
  },
  icon: {
    type: String,
    default: 'mdi-bird'
  }
})

const emit = defineEmits(['select-week', 'reset'])

const {
  calendarWeeks
} = useCalendar()

const internalSelectedWeek = ref(props.selectedWeek)
const isHovering = ref(false)
const showAllWeeks = ref(false)

const visibleWeeks = computed(() => {
  if (!internalSelectedWeek.value || showAllWeeks.value) return calendarWeeks.value
  return calendarWeeks.value.filter(week => {
    const weekStart = week[0]
    return weekStart >= internalSelectedWeek.value[0] && weekStart <= internalSelectedWeek.value[1]
  })
})

const handleSelectWeek = (week) => {
  if (internalSelectedWeek.value && !showAllWeeks.value) {
    showAllWeeks.value = true
    emit('reset')
  } else {
    internalSelectedWeek.value = [week[0], new Date(week[0].getTime() + 6 * 24 * 60 * 60 * 1000)]
    setTimeout(() => {
      showAllWeeks.value = false
      emit('select-week', internalSelectedWeek.value)
    }, 500)
  }
}

const isSelected = (week) => {
  return internalSelectedWeek.value && week[0].getTime() === internalSelectedWeek.value[0].getTime()
}

const formatDateRange = (week) => {
  if (!week || week.length < 2) return '週の選択'
  const start = week[0]
  const end = week[1]
  const options = { year: 'numeric', month: 'long', day: 'numeric' }
  return `${start.toLocaleDateString('ja-JP', options)} - ${end.toLocaleDateString('ja-JP', options)}`
}

const selectedWeekRange = computed(() => {
  return internalSelectedWeek.value ? formatDateRange(internalSelectedWeek.value) : '週の選択'
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
  max-width: 800px;
  padding-top: 0;
}

.hover-effect {
  transition: all 0.3s ease;
  box-shadow: 0 0 15px rgba(100, 149, 237, 0.6) !important;
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