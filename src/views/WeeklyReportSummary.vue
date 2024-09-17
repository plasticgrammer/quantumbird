<template>
  <v-container v-if="!loading">
    <v-row dense class="pb-3">
      <v-col>
        <h3 class="organization-name text-blue-grey-darken-1">
          <v-icon size="large" class="mr-1">
            mdi-domain
          </v-icon>
          {{ organization?.name }}
        </h3>
      </v-col>
    </v-row>

    <v-row dense class="pl-3 pb-4">
      <v-col>
        <h3>
          <v-icon size="large" class="mr-1">
            mdi-calendar-multiple-check
          </v-icon>
          週次報告
          <span v-if="weekString"> ［{{ formatDateRange(getWeekFromString(weekString)) }}］</span>
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
import { getOrganization } from '../services/publicService'
import { verifyToken } from '../services/secureParameterService'
import ReviewForm from '../components/ReviewForm.vue'

const props = defineProps({
  token: {
    type: String,
    required: true
  }
})

const { getWeekFromString, formatDateRange } = useCalendar()

const loading = ref(false)
const organizationId = ref(null)
const weekString = ref(null)
const organization = ref(null)

const showError = inject('showError')

onMounted(async () => {
  loading.value = true
  try {
    const result = await verifyToken(props.token)
    organizationId.value = result.organizationId
    weekString.value = result.weekString
    const org = await getOrganization(organizationId.value)
    if (org && Object.keys(org).length > 0) {
      organization.value = org
    }
    loading.value = false
  } catch (error) {
    if (error?.response?.data === 'Token has expired') {
      showError('リンクの有効期限が切れています', error)
    } else {
      showError('キー情報の取得に失敗しました', error)
    }
  }
})
</script>