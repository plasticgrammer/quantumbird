<template>
  <v-container>
    <WeekSelector
      function-name="週次報告レビュー"
      icon="mdi-calendar-multiple-check"
      :selected-week="selectedWeek"
      @select-week="handleWeekSelection"
      @reset="handleReset"
    />

    <v-alert
      v-if="!isValidWeek"
      type="error"
      class="mt-5"
      outlined
    >
      指定された週は有効範囲外です。
    </v-alert>

    <ReviewForm
      v-if="selectedWeek && isValidWeek"
      :organization-id="organizationId"
      :week-string="getStringFromWeek(selectedWeek)"
    />
  </v-container>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import WeekSelector from '../components/WeekSelector.vue'
import ReviewForm from '../components/ReviewForm.vue'
import { useCalendar } from '../composables/useCalendar'

const props = defineProps({
  weekString: {
    type: String,
    default: null
  }
})

const { getWeekFromString, getStringFromWeek, isWeekInRange } = useCalendar()
const router = useRouter()

const store = useStore()
const organizationId = store.getters['auth/organizationId']
const selectedWeek = ref(null)
const isValidWeek = ref(true)

const handleWeekSelection = (week) => {
  selectedWeek.value = week
  if (week && isWeekInRange(week)) {
    const weekString = getStringFromWeek(week)
    if (weekString) {
      router.push({
        name: 'WeeklyReview',
        params: { weekString: weekString }
      })
      isValidWeek.value = true
    } else {
      isValidWeek.value = false
    }
  } else {
    router.push({ name: 'WeeklyReviewSelector' })
    isValidWeek.value = true
  }
}

const handleReset = () => {
  selectedWeek.value = null
  isValidWeek.value = true
  router.push({ name: 'WeeklyReviewSelector' })
}

watch(() => props.weekString, (newWeekString) => {
  if (newWeekString) {
    const week = getWeekFromString(newWeekString)
    if (week && isWeekInRange(week)) {
      selectedWeek.value = week
      isValidWeek.value = true
    } else {
      selectedWeek.value = null
      isValidWeek.value = false
    }
  } else {
    selectedWeek.value = null
    isValidWeek.value = true
  }
}, { immediate: true })
</script>