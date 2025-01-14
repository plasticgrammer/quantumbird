<template>
  <v-container>
    <v-row>
      <v-col>
        <div class="d-flex align-center mb-4">
          <v-btn
            icon="mdi-arrow-left"
            variant="tonal"
            class="ml-n16 mr-4"
            @click="$router.back()"
          ></v-btn>
          <h3>
            <v-icon size="large" class="mr-1">
              mdi-calendar-range
            </v-icon>
            週次報告履歴<span v-if="memberName">（{{ memberName }}さん）</span>
          </h3>
        </div>

        <v-card class="mb-4" rounded="lg">
          <v-card-title>
            <v-icon icon="mdi-calendar-text-outline" class="mr-1"></v-icon>
            期間の概要
          </v-card-title>
          <v-card-text v-if="totalWeeks" class="px-6">
            <v-row>
              <v-col cols="12" sm="6" md="3">
                <div class="text-subtitle-2 mb-1">対象期間</div>
                <div class="text-h6">
                  {{ formatWeekLabel(firstWeek) }} 〜 {{ formatWeekLabel(lastWeek) }}
                </div>
              </v-col>
              <v-col cols="12" sm="6" md="2">
                <div class="text-subtitle-2 mb-1">報告提出率</div>
                <div class="text-h6">
                  {{ Math.round((submittedReports / totalWeeks) * 100) }}%
                  <span class="text-body-2 text-medium-emphasis">
                    ({{ submittedReports }}/{{ totalWeeks }}週)
                  </span>
                </div>
              </v-col>
              <v-col cols="12" sm="6" md="2">
                <div class="text-subtitle-2 mb-1">平均残業時間</div>
                <div class="text-h6">
                  {{ averageOvertime.toFixed(1) }}
                  <span class="text-body-2">時間/週</span>
                </div>
              </v-col>
              <v-col cols="12" sm="6" md="5">
                <div class="text-subtitle-2 mb-1">最頻プロジェクト</div>
                <div class="text-h6">{{ mostFrequentProject || '該当なし' }}</div>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>

        <ReportSummary
          v-if="weekReports.length > 0"
          :reports="formattedReports"
          class="mb-4"
        />

        <v-card 
          class="my-4"
          rounded="lg"
        >
          <v-card-title>
            <v-icon icon="mdi-chart-line" class="mr-1"></v-icon>
            評価・残業時間推移
          </v-card-title>
          <v-card-text>
            <RatingLineChart
              :chart-data="chartData"
              class="mt-2"
            />
          </v-card-text>
        </v-card>

        <v-tabs
          v-model="selectedWeekTab"
          class="mb-4"
        >
          <v-tab
            v-for="week in weekReports"
            :key="week.weekString"
            :value="week.weekString"
            class="text-body-1"
          >
            {{ formatWeekLabel(week.weekString) }}
          </v-tab>
        </v-tabs>

        <v-window v-model="selectedWeekTab" class="elevation-4 rounded-lg">
          <v-window-item
            v-for="week in weekReports"
            :key="week.weekString"
            :value="week.weekString"
          >
            <v-card v-if="week.report" class="pa-4">
              <template v-if="week.report.status !== 'none'">
                <v-row>
                  <v-col cols="12" md="5">
                    <div class="text-subtitle-1 font-weight-medium mb-2">作業内容</div>
                    <v-list dense class="bg-transparent pa-0">
                      <v-list-item
                        v-for="(project, index) in week.report.projects"
                        :key="index"
                        class="px-2 py-1"
                      >
                        <v-list-item-title>
                          <v-icon small>mdi-folder-outline</v-icon>
                          {{ project.name }}
                        </v-list-item-title>
                        <v-list-item-subtitle class="ml-6">
                          <ul class="work-items-list">
                            <li 
                              v-for="(item, itemIndex) in project.workItems"
                              :key="itemIndex"
                            >
                              {{ item.content }}
                            </li>
                          </ul>
                        </v-list-item-subtitle>
                      </v-list-item>
                    </v-list>

                    <div v-if="week.report.overtimeHours >= 0" class="mt-4">
                      <overtime-display :overtime-hours="week.report.overtimeHours" />
                    </div>
                  </v-col>

                  <v-col cols="12" md="7">
                    <div class="text-subtitle-1 font-weight-medium mb-2">
                      振り返り（成果と課題）
                    </div>
                    <v-textarea
                      v-model="week.report.issues"
                      readonly
                      auto-grow
                      rows="2"
                      hide-details
                      variant="outlined"
                      class="mb-4"
                    />

                    <div class="text-subtitle-1 font-weight-medium mb-2">
                      次の目標、改善施策
                    </div>
                    <v-textarea
                      v-model="week.report.improvements"
                      readonly
                      auto-grow
                      rows="2"
                      hide-details
                      variant="outlined"
                    />
                  </v-col>
                </v-row>
              </template>
              <v-alert
                v-else
                type="info"
                variant="tonal"
              >
                この週の報告はありません
              </v-alert>
            </v-card>
          </v-window-item>
        </v-window>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useCalendar } from '@/composables/useCalendar'
import { listMemberReports } from '@/services/reportService'
import { getMember } from '@/services/memberService'
import OvertimeDisplay from '@/components/OvertimeDisplay.vue'
import RatingLineChart from '@/components/chart/RatingLineChart.vue'
import ReportSummary from '@/components/ReportSummary.vue'

const props = defineProps({
  memberUuid: {
    type: String,
    required: true
  }
})

const calendar = useCalendar()

const memberName = ref('')
const weekReports = ref([])
const selectedWeekTab = ref(null)

const formatWeekLabel = (weekString) => {
  // 古い週から新しい週の順なので、0が5週前、4が先週となる
  const index = weekReports.value.findIndex(report => report.weekString === weekString)
  return calendar.getWeekJpText(-(5 - index))
}

const fetchReports = async () => {
  try {
    const [memberData, reports] = await Promise.all([
      getMember(props.memberUuid),
      listMemberReports(props.memberUuid)
    ])

    if (memberData) {
      memberName.value = memberData.name
    }

    weekReports.value = reports.map(report => ({
      weekString: report.weekString,
      report: report
    }))
    selectedWeekTab.value = reports[reports.length - 1].weekString // 最新の週を選択
  } catch (error) {
    console.error('Failed to fetch reports:', error)
  }
}

const formattedReports = computed(() => {
  return weekReports.value.map(item => ({
    report: {
      ...item.report,
      weekString: formatWeekLabel(item.report.weekString)
    },
  }))
})

const chartData = computed(() => {
  const labels = weekReports.value.map((week, index) => {
    return calendar.getWeekJpText(-(5 - index))
  })
  return {
    labels,
    datasets: [
      {
        label: 'ストレス度',
        data: weekReports.value.map(week => 
          week.report?.status === 'none' ? null : week.report?.rating?.stress || null
        ),
        borderColor: 'rgb(192, 75, 192)',
        backgroundColor: 'rgba(192, 75, 192, 0.2)',
        fill: true,
        yAxisID: 'y'
      },
      {
        label: 'タスク達成度',
        data: weekReports.value.map(week => 
          week.report?.status === 'none' ? null : week.report?.rating?.achievement || null
        ),
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        fill: true,
        yAxisID: 'y'
      },
      {
        label: 'タスク難易度',
        data: weekReports.value.map(week => 
          week.report?.status === 'none' ? null : week.report?.rating?.disability || null
        ),
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.2)',
        fill: true,
        yAxisID: 'y'
      },
      {
        label: '残業時間',
        data: weekReports.value.map(week => 
          week.report?.status === 'none' ? null : week.report?.overtimeHours ?? null
        ),
        borderColor: 'rgb(54, 162, 235)',
        backgroundColor: 'rgba(54, 162, 235, 0.2)',
        fill: true,
        yAxisID: 'y1'
      }
    ]
  }
})

// 統計情報の計算
const firstWeek = computed(() => weekReports.value[0]?.weekString)
const lastWeek = computed(() => weekReports.value[weekReports.value.length - 1]?.weekString)
const totalWeeks = computed(() => weekReports.value.length)
const submittedReports = computed(() => 
  weekReports.value.filter(w => w.report?.status !== 'none').length
)
const averageOvertime = computed(() => {
  const reports = weekReports.value.filter(w => 
    w.report?.status !== 'none' && 
    typeof w.report.overtimeHours === 'number'
  )
  if (!reports.length) return 0
  return reports.reduce((sum, w) => sum + w.report.overtimeHours, 0) / reports.length
})
const mostFrequentProject = computed(() => {
  const projectCounts = {}
  weekReports.value.forEach(week => {
    week.report?.projects?.forEach(project => {
      projectCounts[project.name] = (projectCounts[project.name] || 0) + 1
    })
  })
  return Object.entries(projectCounts)
    .sort(([, a], [, b]) => b - a)[0]?.[0]
})

onMounted(fetchReports)
</script>

<style scoped>
.work-items-list {
  list-style-type: disc;
  padding-left: 20px;
  margin: 4px 0;
}
</style>
