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

    <v-dialog 
      v-model="isReportSubmitted" 
      max-width="460"
    >
      <v-card class="text-center">
        <v-card-title class="text-h5 font-weight-bold">
          週次報告を提出しました
        </v-card-title>
        <v-card-text>
          <v-img
            src="@/assets/images/usagikigurumi.gif"
            max-width="240"
            class="mx-auto mt-0 mb-5"
            :aspect-ratio="1"
          ></v-img>
          <p class="text-body-1">
            報告ありがとうございました。
          </p>
        </v-card-text>
        <v-card-actions class="pb-4">
          <v-row justify="center" no-gutters>
            <v-col cols="auto" class="mx-2">
              <v-btn color="primary" prepend-icon="mdi-chevron-left" variant="elevated" @click="handleBackToReport">
                週次報告に戻る
              </v-btn>
            </v-col>
            <v-col cols="auto" class="mx-2">
              <v-btn color="error" prepend-icon="mdi-close" variant="elevated" @click="handleClose">
                終了する
              </v-btn>
            </v-col>
          </v-row>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, watch, onMounted, defineAsyncComponent } from 'vue'
import { useRouter } from 'vue-router'
import WeekSelector from '../components/WeekSelector.vue'
import ReportForm from '../components/ReportForm.vue'
import { useCalendar } from '../composables/useCalendar'
import { feedbackUrl } from '../config/environment'
import { getMember } from '../services/publicService'

const MemberInfoDialog = defineAsyncComponent(() => import('../components/MemberInfoDialog.vue'))
const StressCheckDialog = defineAsyncComponent(() => import('../components/StressCheckDialog.vue'))

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

const selectedWeek = ref(null)
const isValidWeek = ref(true)
const isReportSubmitted = ref(false)
const member = ref(null)
const memberInfoDialog = ref(null)
const stressCheckDialog = ref(null)

const openMemberInfoDialog = () => {
  memberInfoDialog.value.openDialog()
}

const openStressCheckDialog = () => {
  stressCheckDialog.value.openDialog()
}

const handleStressLevelUpdate = (level) => {
  console.log('Stress level updated:', level)
  // ここでストレスレベルを保存したり、他の処理を行ったりできます
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

  router.push({ 
    name: 'WeeklyReportSelector',
    params: { organizationId: props.organizationId, memberUuid: props.memberUuid }
  })
}

const handleReportSubmitted = () => {
  isReportSubmitted.value = true
}

const handleBackToReport = () => {
  isReportSubmitted.value = false
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
    // 事前ロード
    const img = new Image()
    img.src = require('@/assets/images/usagikigurumi.gif')

    member.value = await getMember(props.memberUuid)
  } catch (err) {
    console.error('Error initializing dashboard:', err)
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