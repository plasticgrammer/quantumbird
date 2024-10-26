```vue
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
      max-width="580"
    >
      <v-card class="text-center">
        <v-card-title class="text-h5 font-weight-bold">
          週次報告ありがとうございました
        </v-card-title>

        <v-card-text class="pt-1">
          <div v-if="isAdviceAvailable">
            <v-img
              :src="advisorRoles[selectedAdvisorRole].image"
              max-width="200"
              class="mx-auto mt-0 mb-3"
              :aspect-ratio="1"
            ></v-img>

            <v-sheet border="info md" class="text-left pa-4 mx-3 rounded-lg">
              <p class="text-caption text-grey-darken-1 mb-2">
                <v-icon 
                  :icon="advisorRoles[selectedAdvisorRole].icon" 
                  :color="advisorRoles[selectedAdvisorRole].color" 
                  size="small" 
                  class="me-1"
                />
                {{ advisorRoles[selectedAdvisorRole].title }}からのアドバイス
              </p>
              <p class="text-body-2 text-grey-darken-3" style="white-space: pre-wrap">
                {{ claudeAdvice }}
              </p>
            </v-sheet>
          </div>

          <!-- アドバイス生成中の表示 -->
          <div v-else-if="isLoadingAdvice">
            <v-img
              :src="advisorRoles[selectedAdvisorRole].image"
              max-width="200"
              class="mx-auto mt-0 mb-3"
              :aspect-ratio="1"
            ></v-img>
            <v-sheet border="info md" class="text-left pa-4 mx-3 rounded-lg">
              <div class="d-flex align-center justify-center py-4">
                <v-skeleton-loader type="paragraph" />
              </div>
            </v-sheet>
          </div>

          <!-- アドバイザー選択UI -->
          <div v-else>
            <v-sheet class="mx-3 mb-2 py-3 advisor-container" variant="outlined">
              <p class="text-body-1">アドバイザーを選んでください</p>
              
              <v-window v-model="selectedAdvisorRole" show-arrows>
                <v-window-item
                  v-for="(advisor, key) in advisorRoles"
                  :key="key"
                  :value="key"
                >
                  <v-card class="mx-2 bg-transparent" elevation="0">
                    <div class="advisor-image-container d-flex align-end justify-center">
                      <v-img
                        :src="advisor.image"
                        max-height="200"
                        max-width="240"
                        class="advisor-image mb-2 mx-auto"
                        :position="'top'"
                      >
                      </v-img>
                    </div>
                    <v-card-item>
                      <v-card-title>
                        <v-icon
                          :icon="advisor.icon"
                          :color="advisor.color"
                          class="me-2"
                        />
                        {{ advisor.title }}
                      </v-card-title>
                      <v-card-subtitle>
                        {{ advisor.description }}
                      </v-card-subtitle>
                    </v-card-item>
                  </v-card>
                </v-window-item>
              </v-window>

              <div class="d-flex justify-center mb-2">
                <v-btn
                  color="primary"
                  variant="outlined"
                  class="px-8"
                  :loading="isLoadingAdvice"
                  @click="generateAdvice"
                >
                  <v-icon icon="mdi-robot" color="info" class="me-2"></v-icon>
                  このアドバイザーに相談する
                </v-btn>
              </div>
            </v-sheet>
          </div>
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
import { advisorRoles, getWeeklyReportAdvice } from '../services/bedrockService'

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
const isLoadingAdvice = ref(false)
const isAdviceAvailable = ref(false)
const claudeAdvice = ref('')
const lastReportContent = ref(null)
const selectedAdvisorRole = ref('manager')

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
  isAdviceAvailable.value = false
  claudeAdvice.value = ''
  lastReportContent.value = null
  selectedAdvisorRole.value = 'manager'

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
  isAdviceAvailable.value = false
  claudeAdvice.value = ''
}

const generateAdvice = async () => {
  if (!lastReportContent.value) return

  try {
    isLoadingAdvice.value = true
    const result = await getWeeklyReportAdvice({
      ...lastReportContent.value,
      advisorRole: {
        role: advisorRoles[selectedAdvisorRole.value].role,
        point: advisorRoles[selectedAdvisorRole.value].point
      }
    })
    claudeAdvice.value = result.advice
    isAdviceAvailable.value = true
  } catch (error) {
    console.error('Error getting weekly report advice:', error)
    claudeAdvice.value = '申し訳ありません。アドバイスの生成中にエラーが発生しました。'
    isAdviceAvailable.value = true
  } finally {
    isLoadingAdvice.value = false
  }
}

const handleBackToReport = () => {
  isReportSubmitted.value = false
  isAdviceAvailable.value = false
  claudeAdvice.value = ''
  lastReportContent.value = null
  selectedAdvisorRole.value = 'manager'
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

.v-window {
  border-radius: 8px;
  overflow: hidden;
}

.v-window-item {
  height: 100%;
}

.advisor-container {
  border: solid 1px #2962ff;
  background-color: #e3f2fd;
}

.advisor-image-container {
  height: 200px;
  overflow: hidden;
  position: relative;
}

.advisor-image {
  width: 100%;
  transition: transform 0.3s ease;
}

.advisor-image-container:hover .advisor-image {
  transform: scale(1.1);
}

.advisor-image :deep(.v-img__img) {
  object-fit: cover !important;
}

.advisor-card {
  transition: transform 0.2s;
}

.advisor-card:hover {
  transform: translateY(-4px);
}
</style>