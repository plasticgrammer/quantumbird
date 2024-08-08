<template>
  <v-container>
    <WeekSelector 
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

    <template v-if="!isReportSubmitted">
      <ReportForm
        v-if="selectedWeek && isValidWeek" 
        :organization-id="organizationId"
        :member-uuid="memberUuid"
        :week-string="getStringFromWeek(selectedWeek)"
        @report-submitted="handleReportSubmitted"
      />
    </template>

    <v-card v-if="isReportSubmitted" class="mt-5 text-center">
      <v-card-title class="text-h5 font-weight-bold">
        週次報告が完了しました
      </v-card-title>
      <v-card-text>
        <v-img
          src="@/assets/images/rakko-1.png"
          max-width="300"
          class="mx-auto my-5"
        ></v-img>
        <p class="text-body-1">
          お疲れ様でした。週次報告が正常に送信されました。
        </p>
      </v-card-text>
      <v-card-actions class="pb-3">
        <v-row justify="center" no-gutters>
          <v-col cols="auto" class="mx-2">
            <v-btn color="primary" prepend-icon="mdi-chevron-left" variant="elevated" @click="handleBackToReport">
              週次報告に戻る
            </v-btn>
          </v-col>
          <v-col cols="auto" class="mx-2">
            <v-btn color="grey" prepend-icon="mdi-close" variant="elevated" @click="handleClose">
              閉じる
            </v-btn>
          </v-col>
        </v-row>
      </v-card-actions>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import WeekSelector from '../components/WeekSelector.vue'
import ReportForm from '../components/ReportForm.vue'
import { useCalendar } from '../composables/useCalendar'

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
</script>