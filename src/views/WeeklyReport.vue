<template>
  <v-container>
    <WeekSelector 
      function-name="週次報告"
      icon="mdi-calendar-week"
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

    <ReportForm
      v-if="selectedWeek && isValidWeek" 
      :organization-id="organizationId"
      :member-uuid="memberUuid"
      :week-string="getStringFromWeek(selectedWeek)"
      @report-submitted="handleReportSubmitted"
    />
    
    <v-btn-group
      v-if="member"
      color="#f6fbff"
      density="comfortable"
      rounded="pill"
      elevation="2"
      divided
      class="me-1 d-none d-md-flex v-btn-group"
    >
      <v-btn
        class="pe-2"
        prepend-icon="mdi-account-circle"
        variant="flat"
        @click="openMemberInfoDialog"
      >
        <div class="text-none font-weight-regular">
          {{ member.name }} さん
        </div>
      </v-btn>
      <v-btn size="small" icon>
        <v-icon icon="mdi-menu-down"></v-icon>
        <v-menu
          activator="parent"
          location="bottom end"
          transition="fade-transition"
        >
          <v-list density="compact" min-width="210" rounded="lg" slim>
            <v-list-item
              prepend-icon="mdi-emoticon-outline"
              title="ストレスチェック"
              link
              @click="openStressCheckDialog"
            ></v-list-item>
            <v-list-item
              prepend-icon="mdi-comment-quote-outline"
              title="フィードバック"
              link
              @click="openFeedbackForm"
            ></v-list-item>
          </v-list>
        </v-menu>
      </v-btn>
    </v-btn-group>

    <MemberInfoDialog
      v-if="member"
      ref="memberInfoDialog"
      v-model:member="member"
    />

    <StressCheckDialog
      ref="stressCheckDialog"
      @stress-level-updated="handleStressLevelUpdate"
    />

    <ReportCompleteDialog
      v-model="isReportSubmitted"
      :report-content="lastReportContent"
      :is-advice-enabled="isAdviceEnabled"
      @back="handleBackToReport"
      @close="handleClose"
    />
  </v-container>
</template>

<script setup>
import { ref, watch, computed, onMounted, defineAsyncComponent } from 'vue'
import { useRouter } from 'vue-router'
import WeekSelector from '../components/WeekSelector.vue'
import ReportForm from '../components/ReportForm.vue'
import { useCalendar } from '../composables/useCalendar'
import { feedbackUrl } from '../config/environment'
import { getOrganization, getMember } from '../services/publicService'

const MemberInfoDialog = defineAsyncComponent(() => import('../components/MemberInfoDialog.vue'))
const StressCheckDialog = defineAsyncComponent(() => import('../components/StressCheckDialog.vue'))
const ReportCompleteDialog = defineAsyncComponent(() => import('../components/ReportCompleteDialog.vue'))

const props = defineProps({
  organizationId: {
    type: String,
    default: null
  },
  memberUuid: {
    type: String,
    default: null
  },
  weekString: {
    type: String,
    default: null
  }
})

const { getWeekFromString, getStringFromWeek, isWeekInRange } = useCalendar()
const router = useRouter()

const organization = ref('')
const selectedWeek = ref(null)
const isValidWeek = ref(true)
const member = ref(null)
const memberInfoDialog = ref(null)
const stressCheckDialog = ref(null)
const isReportSubmitted = ref(false)
const lastReportContent = ref(null)

const isAdviceEnabled = computed(() => {
  return organization.value?.features?.weeklyReportAdvice ?? false
})

const openMemberInfoDialog = () => {
  memberInfoDialog.value.openDialog()
}

const openStressCheckDialog = () => {
  stressCheckDialog.value.openDialog()
}

const handleStressLevelUpdate = (level) => {
  console.log('Stress level updated:', level)
}

const handleWeekSelection = (week) => {
  selectedWeek.value = week
  isReportSubmitted.value = false

  if (week && isWeekInRange(week)) {
    const weekString = getStringFromWeek(week)
    if (weekString) {
      router.push({
        name: 'WeeklyReport',
        params: { organizationId: props.organizationId, memberUuid: props.memberUuid, weekString }
      })
      isValidWeek.value = true
    } else {
      isValidWeek.value = false
    }
  } else {
    router.push({ 
      name: 'WeeklyReportSelector',
      params: { organizationId: props.organizationId, memberUuid: props.memberUuid }
    })
    isValidWeek.value = true
  }
}

const handleReset = () => {
  selectedWeek.value = null
  isValidWeek.value = true
  isReportSubmitted.value = false
  lastReportContent.value = null

  router.push({ 
    name: 'WeeklyReportSelector',
    params: { organizationId: props.organizationId, memberUuid: props.memberUuid }
  })
}

const handleReportSubmitted = async (reportContent) => {
  isReportSubmitted.value = true
  lastReportContent.value = {
    ...reportContent,
    weekString: getStringFromWeek(selectedWeek.value),
    memberUuid: props.memberUuid,
    organizationId: props.organizationId
  }
}

const handleBackToReport = () => {
  isReportSubmitted.value = false
  lastReportContent.value = null
  handleReset()
}

const handleClose = () => {
  window.close()
}

const openFeedbackForm = () => {
  window.open(feedbackUrl, '_blank', 'noopener,noreferrer')
}

watch(() => props.weekString, (newWeekParam) => {
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

onMounted(async () => {
  try {
    const [organizationData, memberData] = await Promise.all([
      getOrganization(props.organizationId),
      getMember(props.memberUuid)
    ])
    
    organization.value = organizationData
    member.value = memberData
  } catch (err) {
    console.error('Error initializing:', err)
  }
})
</script>

<style scoped>
.v-btn-group {
  position: fixed;
  top: 16px;
  right: 16px;
  z-index: 100;
}

@media (max-width: 600px) {
  .v-btn-group {
    display: none;
  }
}
</style>