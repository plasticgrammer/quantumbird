<template>
  <!-- v-mainを使用せず、直接コンテンツを配置 -->
  <div class="about-page">
    <v-container class="pa-0" fluid>
      <!-- ヘッダーセクション -->
      <v-sheet color="menu" class="py-10">
        <v-container class="text-center">
          <div class="logo-font text-h1 pb-10">fluxweek</div>
          <p class="text-h5 font-weight-regular mb-8 text-white">
            ストレスフリーな管理で組織の成果をサポートする週次報告サービス
          </p>
          <v-btn
            color="primary"
            size="x-large"
            to="/signup"
            class="px-8"
          >
            無料で始める
          </v-btn>
        </v-container>
      </v-sheet>

      <!-- 課題セクション -->
      <v-container class="py-16">
        <h2 class="text-h4 font-weight-bold text-center mb-12">こんな課題はありませんか？</h2>
        <v-row>
          <v-col 
            v-for="(problem, i) in problems" 
            :key="i"
            cols="12" md="4" 
          >
            <v-card elevation="2" height="100%">
              <v-card-text class="pa-6">
                <h3 class="text-h6 font-weight-bold primary--text mb-4">{{ problem.title }}</h3>
                <p class="text-body-1">{{ problem.description }}</p>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-container>

      <!-- 特徴セクション -->
      <v-container class="py-16">
        <h2 class="text-h4 font-weight-bold text-center mb-12">fluxweekの特徴</h2>
        <v-row>
          <v-col 
            v-for="(feature, i) in features" 
            :key="i"
            cols="12" md="4" 
          >
            <v-card elevation="2" height="100%">
              <v-card-text class="pa-6">
                <h3 class="text-h6 font-weight-bold primary--text mb-4">{{ feature.title }}</h3>
                <p class="text-body-1">{{ feature.description }}</p>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-container>

      <!-- 料金プランセクション -->
      <v-container class="py-16">
        <h2 class="text-h4 font-weight-bold text-center mb-12">料金プラン</h2>
        <v-row>
          <v-col 
            v-for="plan in pricingPlans" 
            :key="plan.name"
            cols="12" md="4"
          >
            <v-card elevation="2" height="100%" class="price-card">
              <v-card-text class="pa-6 text-center">
                <h3 class="text-h5 font-weight-bold mb-4">{{ plan.name }}</h3>
                <p class="text-h4 font-weight-bold primary--text mb-6">
                  {{ plan.price }}
                  <span v-if="plan.priceUnit" class="text-body-1">/月</span>
                </p>
                <div class="d-flex justify-center">
                  <v-list density="compact" class="features-list text-left">
                    <v-list-item
                      v-for="(feature, i) in plan.features"
                      :key="i"
                    >
                      <template #prepend>
                        <v-icon color="primary">
                          mdi-check-circle
                        </v-icon>
                      </template>
                      {{ feature }}
                    </v-list-item>
                  </v-list>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-container>

      <!-- CTAセクション -->
      <v-sheet color="menu" class="py-10">
        <v-container class="text-center">
          <h2 class="text-h4 font-weight-bold text-white mb-4">
            メンバーの成長をサポートする新しい週次報告を始めましょう
          </h2>
          <p class="text-h6 font-weight-regular text-white mb-8">
            フリープランで、fluxweekの価値を体験してください
          </p>
          <v-btn
            color="primary"
            size="x-large"
            to="/signup"
            class="px-8"
          >
            無料で始める
          </v-btn>
        </v-container>
      </v-sheet>

      <!-- フッター -->
      <v-footer color="grey-darken-3" class="py-8">
        <v-container class="text-center">
          <div class="mb-4">
            <v-btn
              v-for="link in footerLinks"
              :key="link.url"
              :to="link.url"
              variant="text"
              class="text-white mx-2"
            >
              {{ link.text }}
            </v-btn>
          </div>
          <p class="text-white text-body-2">© 2024 fluxweek All rights reserved.</p>
        </v-container>
      </v-footer>
    </v-container>
  </div>
</template>

<script setup>
import { plans } from '@/config/plans'

const problems = [
  {
    title: 'メンバーの状況が見えない',
    description: '週報を受け取っても、本当の課題が把握できない'
  },
  {
    title: '報告が形骸化している',
    description: '形式的な報告で終わり、成長機会を逃している'
  },
  {
    title: 'フィードバックが難しい',
    description: '適切なアドバイスやサポートのタイミングを逃してしまう'
  }
]

const features = [
  {
    title: 'シンプルな入力で自己評価を可視化',
    description: 'ストレス度、タスク難易度、タスク達成度を可視化し、メンバーの状況を素早く把握できます。'
  },
  {
    title: '一元管理と共有機能',
    description: '週次報告とフィードバックを一元管理。Webリンクでの共有も可能です。'
  },
  {
    title: 'AIアドバイザーによる成長支援',
    description: '週次報告の内容を分析し、メンバーの成長をサポートする具体的なアドバイスを提供します。'
  }
]

// プラン情報をplans.jsから生成
const pricingPlans = plans.map(plan => ({
  name: plan.name,
  price: plan.planId === 'free' ? '無料' : `${plan.price.toLocaleString()}円`,
  priceUnit: plan.planId !== 'free',
  features: plan.features
}))

const footerLinks = [
  { text: '利用規約', url: '/legal/terms-of-service' },
  { text: 'プライバシーポリシー', url: '/legal/privacy-policy' },
  { text: '特定商取引法に基づく表記', url: '/legal/specified-commercial-transactions' }
]
</script>

<style scoped>
.price-card :deep(.v-list-item) {
  min-height: 36px;
}
.price-card :deep(.v-list) {
  background-color: transparent;
}

/* シンプル化したスタイル */
.about-page {
  background-color: transparent;
}

/* セクション内のコンテナ幅を制御 */
:deep(.v-container:not(.fluid)) {
  margin: 0 auto;
  padding: 0 24px;
}

@media (max-width: 600px) {
  :deep(.v-container:not(.fluid)) {
    padding: 0 16px;
  }
}

/* 機能リストのスタイル調整 */
.features-list {
  width: fit-content;
  min-width: 200px;
  margin: 0 auto;
}

.features-list :deep(.v-list-item) {
  padding: 0;
}
</style>
