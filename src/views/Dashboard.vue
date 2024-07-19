<template>
  <v-container fluid class="pa-2">
    <v-row dense>
      <v-col cols="12">
        <h1 class="text-h5 mb-2">ダッシュボード</h1>
      </v-col>
    </v-row>

    <v-row dense>
      <v-col cols="12">
        <v-card class="mb-2" elevation="4">
          <v-card-text class="py-5">
            <v-btn
              color="primary"
              :to="{ name: 'OrganizationManagement' }"
              v-if="isAdmin"
              x-small
            >
              <v-icon class="mr-1" small left>mdi-cog</v-icon>
              組織管理
            </v-btn>
            <span class="px-3"/>
            <v-btn
              color="primary"
              :to="{ name: 'WeeklyReviewSelector' }"
              v-if="isAdmin"
              x-small
            >
              <v-icon class="mr-1" small left>mdi-cog</v-icon>
              週次報告管理
            </v-btn>
            <span class="px-3"/>
            <v-btn
              color="secondary"
              :to="{ name: 'WeeklyReportSelector', params: { organizationId: 'jsp-d3g', memberUuid: 'UID0027' } }"
              x-small
            >
              <v-icon class="mr-1" small left>mdi-clipboard-check-outline</v-icon>
              週次報告
            </v-btn>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-row dense>
      <v-col cols="12" md="4">
        <v-card class="mb-2" elevation="4">
          <v-card-title class="text-subtitle-1">
            <v-icon small class="mr-1">mdi-domain</v-icon>
            組織情報
          </v-card-title>
          <v-card-text class="py-1">
            <p class="text-body-2 mb-1">{{ organizationName }}</p>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="4" md="8">
        <v-card class="mb-2" elevation="4">
          <v-card-title class="text-subtitle-1">
            <v-icon small class="mr-1">mdi-clipboard-check</v-icon>
            前週の報告状況
          </v-card-title>
          <v-card-text class="py-1">
            <v-chip x-small class="my-1 mr-2" color="warning" label>
              確認待ち: {{ reportStatus.pending }}
            </v-chip>
            <v-chip x-small class="my-1 mr-2" color="info" label>
              フィードバック中: {{ reportStatus.inFeedback }}
            </v-chip>
            <v-chip x-small class="my-1" color="success" label>
              確認済み: {{ reportStatus.confirmed }}
            </v-chip>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-row dense>
      <v-col cols="12">
        <v-card elevation="4">
          <v-card-title class="text-subtitle-1">
            <v-icon small class="mr-1">mdi-chart-line</v-icon>
            個人別残業時間の遷移（過去5週間）
          </v-card-title>
          <v-card-text>
            <canvas ref="overtimeChart" height="200"></canvas>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { ref, onMounted } from 'vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

export default {
  name: 'Dashboard',
  setup() {
    const organizationName = ref('サンプル株式会社')
    const isAdmin = ref(true)
    const reportStatus = ref({
      pending: 5,
      inFeedback: 3,
      confirmed: 12
    })

    const overtimeChart = ref(null)
    
    const overtimeData = {
      labels: ['5週間前', '4週間前', '3週間前', '2週間前', '先週'],
      datasets: [
        {
          label: '田中太郎',
          data: [2, 5, 3, 4, 5],
          borderColor: 'rgb(75, 192, 192)',
          tension: 0.1
        },
        {
          label: '佐藤花子',
          data: [1, 3, 6, 2, 0],
          borderColor: 'rgb(255, 99, 132)',
          tension: 0.1
        },
        {
          label: '鈴木一郎',
          data: [4, 2, 5, 3, 0],
          borderColor: 'rgb(255, 205, 86)',
          tension: 0.1
        }
      ]
    }

    onMounted(() => {
      const ctx = overtimeChart.value.getContext('2d')
      new Chart(ctx, {
        type: 'line',
        data: overtimeData,
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'top',
            },
            title: {
              display: false
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              title: {
                display: true,
                text: '残業時間'
              }
            }
          }
        }
      })
    })

    return {
      organizationName,
      isAdmin,
      reportStatus,
      overtimeChart,
      overtimeData
    }
  }
}
</script>

<style scoped>
.calendar-small :deep(.v-date-picker-month) {
  height: 240px;
}

.calendar-small :deep(.v-date-picker-month__day) {
  width: 28px;
  height: 28px;
  font-size: 0.9rem;
}

.calendar-small :deep(.v-date-picker-controls) {
  display: none;
}
</style>