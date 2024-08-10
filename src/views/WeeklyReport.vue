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
    
    <v-speed-dial
      location="bottom right"
      transition="fade-transition"
    >
      <template #activator="{ props: activatorProps }">
        <v-fab
          v-if="member"
          v-bind="activatorProps"
          color="surface-variant"
          variant="tonal"
          class="me-1"
          location="top end"
          size="large"
          extended
          :text="`${ member.name }さん`"
          sticky
          app
        >
          <template #prepend>
            <v-icon size="x-large">
              mdi-account-circle
            </v-icon>
          </template>
        </v-fab>
      </template>

      <v-list
        key="1"
        :lines="false"
        density="compact"
      >
        <v-list-subheader></v-list-subheader>
        <v-list-item
          v-for="(item, i) in [{icon:'mdi-cog', text:'設定'}]"
          :key="i"
          :value="item"
          color="primary"
        >
          <v-list-item-title>
            <v-icon :icon="item.icon" class="mr-2"></v-icon>
            {{ item.text }}
          </v-list-item-title>
        </v-list-item>
      </v-list>
    </v-speed-dial>

    <v-dialog 
      v-model="isReportSubmitted" 
      max-width="460"
    >
      <v-card class="text-center">
        <v-card-title class="text-h5 font-weight-bold">
          週次報告が完了しました
        </v-card-title>
        <v-card-text>
          <v-img
            src="@/assets/images/usagikigurumi-1.gif"
            max-width="240"
            class="mx-auto mt-0 mb-5"
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
              <v-btn color="#B00020" prepend-icon="mdi-close" variant="elevated" @click="handleClose">
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
import { ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import WeekSelector from '../components/WeekSelector.vue'
import ReportForm from '../components/ReportForm.vue'
import { useCalendar } from '../composables/useCalendar'
import { getMember } from '../services/memberService'

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
  // ウィンドウを閉じる処理を実装
  window.close()
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