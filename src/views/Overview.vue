<template>
  <v-container class="content-container">
    <v-alert
      :icon="isMobile ? undefined : 'mdi-comment-text'"
      class="mx-auto mt-8 mb-12 border-md text-center"
      color="blue-lighten-5"
      max-width="600"
      min-height="100"
      variant="flat"
      :closable="!isMobile"
    >
      <v-container 
        v-if="!isLoading"
        class="text-body-1 px-0"
      >
        <p v-if="organization.members.length == 0">
          最初に組織情報の登録が必要です。<br>
          <v-btn
            color="black"
            variant="outlined"
            :to="{ name: 'OrganizationManagement' }"
            class="mt-3"
          >
            <v-icon class="mr-1" small>
              mdi-domain
            </v-icon>
            組織情報管理
          </v-btn>
        </p>
        <p v-else-if="!organization.requestEnabled">
          報告依頼の自動送信がオフとなっています。<br>
          <v-btn
            color="black"
            variant="outlined"
            :to="{ name: 'RequestSetting' }"
            class="mt-3"
          >
            <v-icon class="mr-1" small>
              mdi-mail
            </v-icon>
            報告依頼設定
          </v-btn>
        </p>
        <p v-else-if="reportStatus['pending'].count">
          先週分の確認待ちの報告があります。<br>
          <v-badge 
            color="info"
            :content="reportStatus['pending'].count"
            class="mt-3"
          >
            <v-btn 
              color="black"
              variant="outlined"
              :to="{ name: 'WeeklyReview', params: { weekString } }" 
            >
              <v-icon class="mr-1" small left>
                mdi-calendar-multiple-check
              </v-icon>
              週次報告レビュー
            </v-btn>
          </v-badge>
        </p>
        <p v-else>
          各種状況を確認してください。<br>
          <v-btn
            color="black"
            variant="outlined"
            :to="{ name: 'Dashboard' }"
            class="mt-3"
          >
            <v-icon class="mr-1" small>
              mdi-view-dashboard
            </v-icon>
            ダッシュボード
          </v-btn>
        </p>
      </v-container>
      <div v-else>
        <v-progress-circular 
          size="42"
          width="8"
          indeterminate
        ></v-progress-circular>
      </div>
    </v-alert>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useCalendar } from '../composables/useCalendar'
import { useResponsive } from '../composables/useResponsive'
import { getOrganization } from '../services/organizationService'
import { getReportStatus } from '../services/reportService'

const store = useStore()
const organizationId = store.getters['auth/organizationId']
const { getPreviousWeekString } = useCalendar()
const { isMobile } = useResponsive()

const isLoading = ref(true)
const error = ref(null)
const organization = ref('')
const reportStatus = ref('')
const weekString = ref('')

const fetchOrganizationInfo = async () => {
  try {
    const org = await getOrganization(organizationId)
    organization.value = org
  } catch (err) {
    console.error('Failed to fetch organization info:', err)
    error.value = '組織情報の取得に失敗しました'
  }
}

const fetchReportStatus = async () => {
  try {
    weekString.value = getPreviousWeekString()
    const status = await getReportStatus(organizationId, weekString.value)
    reportStatus.value = {
      ...status,
      reportedCount: status.pending.count + status.inFeedback.count + status.confirmed.count
    }
  } catch (err) {
    console.error('Failed to fetch report status:', err)
    error.value = '報告状況の取得に失敗しました: ' + err.message
    throw err
  }
}

const fetchAll = async () => {
  isLoading.value = true
  try {
    await Promise.all([
      fetchOrganizationInfo(),
      fetchReportStatus()
    ])
    // initChart の呼び出しを削除
  } catch (err) {
    console.error('Error initializing dashboard:', err)
    error.value = '初期化に失敗しました'
  } finally {
    isLoading.value = false
  }
}

onMounted(fetchAll)
</script>
