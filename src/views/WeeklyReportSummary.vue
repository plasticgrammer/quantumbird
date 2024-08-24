<template>
  <v-container>
    <v-row dense class="pb-4">
      <v-col>
        <h3>
          <v-icon size="large" class="mr-1">
            mdi-calendar-multiple-check
          </v-icon>
          週次報告 ［{{ formatDateRange(getWeekFromString(weekString)) }}］
        </h3>
      </v-col>
    </v-row>

    <ReviewForm
      v-if="organizationId && weekString"
      :organization-id="organizationId"
      :week-string="weekString"
      :readonly="true"
    />
  </v-container>
</template>

<script setup>
import { ref, inject, onMounted } from 'vue'
import { useCalendar } from '../composables/useCalendar'
import { verifyToken } from '../services/secureParameterService'
import ReviewForm from '../components/ReviewForm.vue'

const props = defineProps({
  token: {
    type: String,
    required: true
  }
})

const { 
  getWeekFromString,
  formatDateRange
} = useCalendar()

const loading = ref(false)
const organizationId = ref(null)
const weekString = ref(null)
const showNotification = inject('showNotification')

onMounted(async () => {
  loading.value = true
  try {
    const result = await verifyToken(props.token)
    organizationId.value = result.organizationId
    weekString.value = result.weekString
  } catch (error) {
    showNotification('キー情報の取得に失敗しました', error)
  } finally {
    loading.value = false
  }
})
</script>