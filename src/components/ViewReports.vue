<template>
  <v-container>
    <h1 class="text-h4 font-weight-bold mb-4">週次報告確認</h1>
    <v-row>
      <v-col v-for="report in reports" :key="report.id" cols="12" md="6">
        <v-card
          :class="{ 'approved-card': report.status === 'approved' }"
          :elevation="2"
        >
          <v-card-title class="d-flex justify-space-between align-center">
            <span class="text-h5 font-weight-bold blue--text">{{ report.name }}</span>
            <v-chip small>
              <v-icon left small>mdi-clock-outline</v-icon>
              残業: {{ report.overtime }}時間
            </v-chip>
          </v-card-title>

          <v-card-text>
            <v-row>
              <v-col cols="6">
                <h3 class="font-weight-bold mb-2">プロジェクト:</h3>
                <div v-for="(project, index) in report.projects" :key="index" class="mb-2">
                  <div class="d-flex align-center">
                    <v-icon small class="mr-1">mdi-briefcase</v-icon>
                    <span class="font-weight-medium">{{ project.name }}</span>
                  </div>
                  <p class="ml-4 text-caption">{{ project.tasks }}</p>
                </div>
              </v-col>
              <v-col cols="6">
                <div class="mb-3">
                  <h3 class="font-weight-bold mb-1 d-flex align-center">
                    <v-icon small class="mr-1">mdi-trophy</v-icon>
                    成果:
                  </h3>
                  <p class="text-caption">{{ report.achievements }}</p>
                </div>
                <div>
                  <h3 class="font-weight-bold mb-1 d-flex align-center">
                    <v-icon small class="mr-1">mdi-alert</v-icon>
                    問題点:
                  </h3>
                  <p class="text-caption">{{ report.issues }}</p>
                </div>
              </v-col>
            </v-row>

            <v-textarea
              v-if="report.status !== 'approved'"
              v-model="report.feedback"
              label="フィードバックを入力..."
              rows="2"
              class="mt-3"
            ></v-textarea>

            <v-alert
              v-if="report.status === 'approved'"
              type="success"
              dense
              text
              class="mt-3"
            >
              <div class="d-flex align-center">
                承認済み: {{ report.approvedAt }}
              </div>
            </v-alert>

            <v-alert
              v-if="report.status === 'feedback'"
              type="warning"
              dense
              text
              class="mt-3"
            >
              <div class="font-weight-bold">フィードバック:</div>
              <p>{{ report.feedback }}</p>
            </v-alert>
          </v-card-text>

          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn
              v-if="report.status !== 'approved'"
              color="primary"
              @click="handleApprove(report.id)"
              small
            >
              <v-icon left small>mdi-thumb-up</v-icon>
              承認
            </v-btn>
            <v-btn
              v-if="report.status !== 'approved'"
              color="warning"
              @click="submitFeedback(report.id)"
              :disabled="!report.feedback.trim()"
              class="ml-2"
              small
            >
              <v-icon left small>mdi-message</v-icon>
              フィードバック送信
            </v-btn>
            <v-chip small>
              {{ getStatusText(report.status) }}
            </v-chip>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  data() {
    return {
      reports: [
        {
          id: 1,
          name: "田中太郎",
          projects: [
            { name: "プロジェクトA", tasks: "設計完了、実装着手" },
            { name: "プロジェクトB", tasks: "テスト計画作成" }
          ],
          overtime: 5,
          achievements: "プロジェクトAの設計を予定通り完了",
          issues: "プロジェクトBのリソース不足",
          status: "approved",
          feedback: "",
          approvedAt: "2024-07-08 14:30"
        },
        {
          id: 2,
          name: "佐藤花子",
          projects: [
            { name: "プロジェクトC", tasks: "要件定義更新、クライアントミーティング" }
          ],
          overtime: 3,
          achievements: "クライアントから新要件の承認を得た",
          issues: "スケジュールの遅れが懸念される",
          status: "pending",
          feedback: ""
        },
        {
          id: 3,
          name: "鈴木一郎",
          projects: [
            { name: "プロジェクトD", tasks: "コードレビュー、バグ修正" },
            { name: "プロジェクトE", tasks: "新機能の設計" }
          ],
          overtime: 2,
          achievements: "重要なバグを修正し、顧客満足度が向上",
          issues: "新機能の設計に予想以上に時間がかかっている",
          status: "feedback",
          feedback: "新機能の設計遅延について、具体的な原因と対策を教えてください。"
        }
      ]
    };
  },
  methods: {
    handleApprove(id) {
      const now = new Date();
      this.reports = this.reports.map(report =>
        report.id === id
          ? { ...report, status: "approved", feedback: "", approvedAt: now.toLocaleString() }
          : report
      );
    },
    submitFeedback(id) {
      const report = this.reports.find(r => r.id === id);
      if (report && report.feedback.trim() !== "") {
        this.reports = this.reports.map(r =>
          r.id === id ? { ...r, status: "feedback" } : r
        );
      }
    },
    getStatusText(status) {
      switch (status) {
        case "pending":
          return "保留中";
        case "approved":
          return "承認済み";
        case "feedback":
          return "フィードバック済み";
        default:
          return "";
      }
    }
  }
};
</script>

<style scoped>
.approved-card {
  background-color: #e8f6f3 !important;
  border: 1px solid #2ecc71;
}
</style>