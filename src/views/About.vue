<template>
  <div class="about-page">
    <v-container class="pa-0" fluid>
      <!-- ヘッダーセクション -->
      <v-container class="hero-section text-center py-13">
        <p class="text-h4 font-weight-bold text-indigo-darken-2 slide-up-delay hero-text">
          ストレスフリーな管理で<br>組織の成果をサポートする週次報告サービス<br>
          <span class="logo-font text-h2 my-5">fluxweek</span>
        </p>
        <v-img
          src="@/assets/images/rakko.webp"
          class="mx-auto my-4 hero-image"
        ></v-img>
        <v-btn
          color="primary"
          size="x-large"
          to="/signup"
          class="px-8 elevation-4"
          rounded="pill"
        >
          無料で始める
          <v-icon end>mdi-arrow-right</v-icon>
        </v-btn>
        <div class="mt-6">
          アカウントをお持ちの方はこちらから
          <router-link to="/signin">サインイン</router-link>
        </div>
      </v-container>

      <!-- 課題セクション -->
      <v-container class="py-16">
        <h2 class="text-h4 font-weight-bold text-center mb-16 gradient-text">こんな課題はありませんか？</h2>
        <v-row>
          <v-col 
            v-for="(problem, i) in problems" 
            :key="i"
            cols="12" md="4" 
          >
            <v-card elevation="4" height="100%" rounded="lg" hover>
              <v-card-text class="pa-8">
                <div class="d-flex align-center mb-4">
                  <v-icon size="32" color="primary" class="mr-4">{{ problem.icon }}</v-icon>
                  <h3 class="text-h6 font-weight-bold">{{ problem.title }}</h3>
                </div>
                <p class="text-body-1">{{ problem.description }}</p>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-container>

      <!-- 特徴セクション -->
      <v-container class="py-16">
        <h2 class="text-h4 font-weight-bold text-center mb-16 gradient-text">サービスの特徴</h2>
        <v-row>
          <v-col 
            v-for="(feature, i) in features" 
            :key="i"
            cols="12" md="4" 
          >
            <v-card elevation="2" height="100%" rounded="lg" hover class="feature-card">
              <v-card-text class="pa-8">
                <div class="feature-icon mb-6">
                  <v-icon size="36" color="primary">{{ feature.icon }}</v-icon>
                </div>
                <h3 class="text-h6 font-weight-bold mb-4">{{ feature.title }}</h3>
                <p class="text-body-1">{{ feature.description }}</p>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-container>

      <!-- 画面イメージセクション -->
      <v-container class="py-16">
        <h2 class="text-h4 font-weight-bold text-center mb-16 gradient-text">主な機能と画面</h2>
        <v-carousel
          cycle
          progress="primary"
          show-arrows="hover"
          height="840"
          class="elevation-4 rounded-lg"
        >
          <v-carousel-item
            v-for="(screen, i) in screenImages"
            :key="i"
          >
            <v-sheet class="d-flex align-center justify-center pb-8" height="100%">
              <div class="text-center" style="width: 100%;">
                <v-img
                  :src="screen.image"
                  :alt="screen.title"
                  class="mx-auto mb-4"
                  max-height="680"
                  contain
                ></v-img>
                <h3 class="text-h5 font-weight-bold mb-2">{{ screen.title }}</h3>
                <p class="text-body-1">{{ screen.description }}</p>
              </div>
            </v-sheet>
          </v-carousel-item>
        </v-carousel>
      </v-container>
      
      <!-- 料金プランセクション -->
      <v-container class="py-16">
        <h2 class="text-h4 font-weight-bold text-center mb-16 gradient-text">料金プラン</h2>
        <v-row>
          <v-col 
            v-for="plan in pricingPlans" 
            :key="plan.name"
            cols="12" md="4"
          >
            <v-card elevation="2" height="100%" rounded="lg" class="price-card">
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
      <v-sheet color="menu" class="py-10 mt-16">
        <v-container class="text-center">
          <h2 class="text-h5 font-weight-bold text-white mb-4">
            メンバーの成長をサポートする新しい週次報告を始めましょう
          </h2>
          <p class="text-h6 font-weight-regular text-white mb-8">
            フリープランで fluxweek の価値を体験してください
          </p>
          <v-btn
            color="primary"
            size="x-large"
            to="/signup"
            class="px-8 elevation-4"
            rounded="pill"
          >
            無料で始める
            <v-icon end>mdi-arrow-right</v-icon>
          </v-btn>
          <div class="mt-6">
            アカウントをお持ちの方はこちらから
            <router-link to="/signin" class="text-white">サインイン</router-link>
          </div>
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
import { onMounted } from 'vue'
import { plans } from '@/config/plans'

const problems = [
  {
    title: 'メンバーの状況が見えない',
    description: '週報を受け取っても、本当の課題が把握できない',
    icon: 'mdi-eye-off'
  },
  {
    title: '報告が形骸化している',
    description: '形式的な報告で終わり、成長機会を逃している',
    icon: 'mdi-format-list-checks'
  },
  {
    title: 'フィードバックが難しい',
    description: '適切なアドバイスやサポートのタイミングを逃してしまう',
    icon: 'mdi-message-alert'
  }
]

const features = [
  {
    title: 'シンプルな入力で自己評価を可視化',
    description: 'ストレス度、タスク難易度、タスク達成度を可視化し、メンバーの状況を素早く把握できます。',
    icon: 'mdi-chart-line'
  },
  {
    title: '一元管理と共有機能',
    description: '週次報告とフィードバックを一元管理。Webリンクでの共有も可能です。',
    icon: 'mdi-share-variant'
  },
  {
    title: 'AIアドバイザーによる成長支援',
    description: '週次報告の内容を分析し、メンバーの成長をサポートする具体的なアドバイスを提供します。',
    icon: 'mdi-robot'
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

const screenImages = [
  {
    image: require('@/assets/images/screenshot/a1_dashborad.png'),
    title: 'ダッシュボード',
    description: 'チームの状況を一目で把握できるダッシュボード画面'
  },
  {
    image: require('@/assets/images/screenshot/b1_report.png'),
    title: '組織メンバーの週次報告',
    description: 'シンプルで使いやすい週次報告入力フォーム'
  },
  {
    image: require('@/assets/images/screenshot/b2_advice.png'),
    title: 'AIアドバイザー機能',
    description: '週次報告の内容を分析し、複数の視点から具体的なアドバイスを提供'
  },
  {
    image: require('@/assets/images/screenshot/a2_organization.png'),
    title: '組織情報管理',
    description: 'メンバーと組織の情報をシンプルに管理'
  },
  {
    image: require('@/assets/images/screenshot/a3_request.png'),
    title: '週次報告設定',
    description: '組織に合わせた週次報告の設定が可能'
  },
  {
    image: require('@/assets/images/screenshot/a4_review.png'),
    title: '週次報告レビュー',
    description: 'メンバーの週次報告を効率的にレビュー'
  },
]

// プリロード用のユーティリティ関数
const preloadImage = (src) => {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.onload = () => resolve(img)
    img.onerror = reject
    img.src = src
  })
}

// 画像のプリロード処理
const preloadScreenshots = async () => {
  try {
    await Promise.all(screenImages.map(screen => preloadImage(screen.image)))
    console.log('All screenshots preloaded successfully')
  } catch (error) {
    console.error('Error preloading screenshots:', error)
  }
}

// コンポーネントマウント時にプリロード開始
onMounted(() => {
  preloadScreenshots()
})
</script>

<style>
#main-content {
  padding-bottom: 0px !important;
}
</style>

<style scoped>
/* ヒーローセクション */
.hero-section {
  position: relative;
  overflow: hidden;
  margin-top: -64px; /* ヘッダーの高さ分を相殺 */
  padding-top: 64px;
}

.hero-section > * {
  position: relative;
  z-index: 2;
}

.hero-text {
  line-height: 1.5;
  letter-spacing: 0.1em !important;
}

.hero-image {
  height: 230px;
}

.price-card :deep(.v-list-item) {
  min-height: 36px;
}
.price-card :deep(.v-list) {
  background-color: transparent;
}

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

/* レスポンシブ対応 */
@media (max-width: 600px) {
  :deep(.v-carousel) {
    height: 460px !important;
  }
}

/* グラデーションテキスト */
.gradient-text {
  background: linear-gradient(45deg, rgb(25, 118, 210), rgb(41, 182, 246));
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  color: transparent;
  width: 100%;
  text-align: center;
}

/* 特徴カード */
.feature-card {
  transition: transform 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-5px);
}

.feature-icon {
  background: linear-gradient(45deg, var(--v-primary-lighten-4), var(--v-primary-lighten-5));
  width: 64px;
  height: 64px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
