<template>
  <v-container>
    <WeekSelector
      :selectedWeek="selectedWeek"
      :isLocked="!!selectedWeek"
      @select-week="handleWeekSelection"
      @reset="handleReset"
    />

    <v-alert v-if="!isValidWeek" type="error" class="mt-5" outlined>
      指定された週は有効範囲外です。
    </v-alert>

    <ReviewForm v-if="selectedWeek && isValidWeek"
      :selectedWeek="selectedWeek"/>

  </v-container>
</template>

<script>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import WeekSelector from '../components/WeekSelector.vue'
import ReviewForm from '../components/ReviewForm.vue'
import { useCalendar } from '../composables/useCalendar'

export default {
  name: 'WeeklyReview',
  components: {
    WeekSelector,
    ReviewForm
  },
  props: {
    weekParam: {
      type: String,
      default: null
    }
  },
  setup(props) {
    const { getWeekFromString, getStringFromWeek, isWeekInRange } = useCalendar()
    const router = useRouter()

    const selectedWeek = ref(null)
    const isValidWeek = ref(true)

    const handleWeekSelection = (week) => {
      selectedWeek.value = week
      if (week && isWeekInRange(week)) {
        const weekString = getStringFromWeek(week)
        if (weekString) {
          router.push({
            name: 'WeeklyReview',
            params: { weekParam: weekString }
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

    watch(() => props.weekParam, (newWeekParam) => {
      if (newWeekParam) {
        const week = getWeekFromString(newWeekParam)
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

    return {
      selectedWeek,
      isValidWeek,
      handleWeekSelection,
      handleReset
    }
  }
}
</script>