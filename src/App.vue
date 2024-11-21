<template>
  <v-app id="main" aria-label="Main application">
    <template v-if="showAnimation">
      <div class="wave-container">
        <div class="wave"></div>
        <div class="wave"></div>
        <v-img
          v-if="!isMobile"
          src="@/assets/images/rakko.webp"
          width="340"
          class="on-wave mx-auto"
          :style="bgImageStyle"
          alt="Cute sea otter mascot floating on waves"
          loading="lazy"
        ></v-img>
      </div>
    </template>

    <!-- Notification snackbar -->
    <v-snackbar
      v-model="notification.show"
      :color="getNotificationColor"
      :timeout="5000"
      location="top"
      max-width="960px"
      :width="`calc(100vw - ${navigationWidth + 20}px)`"
      class="custom-snackbar"
      role="alert"
      aria-live="assertive"
    >
      <div class="text-subtitle-1 d-flex align-center py-1">
        <v-icon
          :icon="getNotificationIcon"
          class="mr-2"
          color="white"
          aria-hidden="true"
        />
        {{ notification.message }}
      </div>
      <template #actions>
        <v-btn
          color="white"
          variant="text"
          icon="mdi-close"
          aria-label="Close notification"
          @click="closeNotification"
        >
        </v-btn>
      </template>
    </v-snackbar>

    <!-- Navigation drawer -->
    <template v-if="showNavigation">
      <v-navigation-drawer
        v-if="!isMobile"
        v-model="drawer"
        :rail="isRailModeActive"
        permanent
        location="left"
        :width="255"
        color="menu"
        class="navigation-drawer d-print-none"
        aria-label="Main navigation"
        @mouseenter="isHovered = true"
        @mouseleave="isHovered = false"
      >
        <v-list role="menu">
          <v-list-item class="dense-list-item pr-2">
            <template #prepend>
              <v-icon 
                v-ripple
                icon="mdi-menu"
                class="opacity-100 mr-1 my-3"
                role="button"
                aria-label="Toggle drawer mode"
                tabindex="0"
                @click="toggleDrawerMode"
              ></v-icon>
            </template>
            <v-list-item-title>
              <v-img
                src="@/assets/logo.png"
                class="cursor-pointer mr-2"
                alt="application logo"
                role="link"
                aria-label="Go to Overview"
                tabindex="0"
                loading="lazy"
                @click="navigateTo({ name: 'Overview' })"
              ></v-img>
            </v-list-item-title>
            <template #append>
              <v-icon 
                :icon="isRailMode ? 'mdi-format-horizontal-align-right' : 'mdi-format-horizontal-align-left'"
                role="button"
                :aria-label="isRailMode ? 'Expand drawer' : 'Collapse drawer'"
                tabindex="0"
                @click="toggleDrawerMode"
              ></v-icon>
            </template>
          </v-list-item>
        </v-list>
        <v-divider></v-divider>
        <v-list nav role="menu">
          <v-list-item
            v-for="item in navigationItems"
            :key="item.value"
            :prepend-icon="item.icon"
            :value="item.value"
            role="menuitem"
            :aria-label="item.title"
            @click="navigateTo(item.route)"
          >
            <v-list-item-title class="pl-2">{{ item.title }}</v-list-item-title>
          </v-list-item>
        </v-list>

        <!-- User menu -->
        <template #append>
          <v-divider />
          <UserMenu v-model="showUserMenu" bg-color="menu" />
        </template>
      </v-navigation-drawer>

      <!-- Mobile bottom navigation -->
      <v-bottom-navigation
        v-else
        bg-color="menu"
        class="d-print-none"
        grow
        role="navigation"
        aria-label="Mobile navigation"
      >
        <v-btn
          v-for="item in navigationItems"
          :key="item.value"
          :value="item.value"
          :aria-label="item.title"
          class="pb-3"
          @click="navigateTo(item.route)"
        >
          <v-icon size="x-large" aria-hidden="true">
            {{ item.icon }}
          </v-icon>
        </v-btn>
      </v-bottom-navigation>
    </template>

    <!-- Main content area -->
    <v-main :class="{ 'noshift': isRailModeActive }" :style="appStyle" role="main">
      <div class="content-wrapper">
        <router-view />
      </div>
    </v-main>

    <!-- Confirmation dialog -->
    <ConfirmationDialog ref="confirmDialog" />
    <!-- Loading overlay -->
    <LoadingOverlay :style="bgImageStyle" />
    <!-- Policy Acceptance Dialog -->
    <PolicyAcceptanceDialog
      v-model="showPolicyDialog"
      :needs-tos-acceptance="needsTosAcceptance"
      :needs-privacy-policy-acceptance="needsPrivacyPolicyAcceptance"
      @accept="handlePolicyAcceptance"
      @disaccept="handlePolicyDisacceptance"
    />
  </v-app>
</template>

<script setup>
import { ref, provide, reactive, computed, watch, onMounted, defineAsyncComponent } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { useResponsive } from './composables/useResponsive'
import UserMenu from './components/UserMenu.vue'

const ConfirmationDialog = defineAsyncComponent(() => import('./components/ConfirmationDialog.vue'))
const LoadingOverlay = defineAsyncComponent(() => import('./components/LoadingOverlay.vue'))
const PolicyAcceptanceDialog = defineAsyncComponent(() => import('./components/PolicyAcceptanceDialog.vue'))

const router = useRouter()
const store = useStore()
const { isMobile } = useResponsive()

const confirmDialog = ref(null)
const drawer = ref(true)
const isRailMode = ref(true)
const isHovered = ref(false)
const showAnimation = ref(true)
const showNavigation = ref(true)
const showPolicyDialog = ref(false)
const showUserMenu = ref(false)
const needsTosAcceptance = ref(false)
const needsPrivacyPolicyAcceptance = ref(false)
const isPolicyCheckPending = ref(true)
const isAuthenticated = computed(() => store.getters['auth/isAuthenticated'])

router.beforeEach((to, from, next) => {
  showAnimation.value = !to.meta.hideAnimation
  showNavigation.value = !to.meta.hideNavigation
  next()
})

const isRailModeActive = computed(() => !isMobile.value && isRailMode.value && !(isHovered.value || showUserMenu.value))
const navigationWidth = computed(() => isRailModeActive.value ? 56 : 255)

const appStyle = computed(() => ({
  paddingBottom: (router.currentRoute.value.meta.hideAnimation ? 30 : 260) + 'px'
}))

const bgImageStyle = computed(() => ({
  marginLeft: (isMobile.value || router.currentRoute.value.meta.hideNavigation 
    ? 20 
    : 20 + navigationWidth.value / 2) + 'px !important',
  bottom: (isMobile.value ? 30 : -10) + 'px !important'
}))

const toggleDrawerMode = () => {
  isRailMode.value = !isRailMode.value
  isHovered.value = false
}

const navigationItems = [
  { 
    icon: 'mdi-view-dashboard', 
    title: 'ダッシュボード', 
    value: 'Dashboard', 
    route: { name: 'Dashboard' }
  },
  { 
    icon: 'mdi-calendar-multiple-check', 
    title: '週次報告レビュー', 
    value: 'WeeklyReview', 
    route: { name: 'WeeklyReviewSelector' }
  },
  { 
    icon: 'mdi-domain', 
    title: '組織情報管理', 
    value: 'Organization', 
    route: { name: 'OrganizationManagement' }
  },
  { 
    icon: 'mdi-mail', 
    title: '報告依頼設定', 
    value: 'RequestSetting', 
    route: { name: 'RequestSetting' }
  },
]

const notification = reactive({
  show: false,
  type: 'success',
  message: ''
})

const getNotificationIcon = computed(() => {
  switch (notification.type) {
  case 'success': return 'mdi-check-circle'
  case 'error': return 'mdi-alert-circle'
  case 'warning': return 'mdi-alert'
  case 'info': return 'mdi-information'
  default: return 'mdi-bell'
  }
})

const getNotificationColor = computed(() => {
  switch (notification.type) {
  case 'error': return 'error'
  case 'warning': return 'warning'
  default: return 'info'
  }
})

const showNotification = (message, type, error = false) => {
  notification.show = true
  notification.type = type || 'success'
  notification.message = message
  if (error) {
    console.error(error)
  }
}

const showError = (message, error) => {
  showNotification(message, 'error', error)
}

const closeNotification = () => {
  notification.show = false
}

const showConfirmDialogGlobal = async (title, message) => {
  if (!confirmDialog.value) {
    console.error('Confirmation dialog component not found')
    return false
  }
  try {
    return await confirmDialog.value.open(title, message)
  } catch (error) {
    console.error('Error showing confirmation dialog:', error)
    return false
  }
}

provide('showConfirmDialog', showConfirmDialogGlobal)
provide('showNotification', showNotification)
provide('showError', showError)

const navigateTo = (route, params = {}) => {
  router.push({ ...route, params: { ...route.params, ...params } })
  if (isMobile.value) {
    drawer.value = false
  }
}

const checkPolicies = async () => {
  if (!isAuthenticated.value) {
    isPolicyCheckPending.value = false
    return
  }

  try {
    const { needsTosAcceptance: needsTos, needsPrivacyPolicyAcceptance: needsPrivacy } = 
      await store.dispatch('auth/checkPolicyAcceptance')
    
    needsTosAcceptance.value = needsTos
    needsPrivacyPolicyAcceptance.value = needsPrivacy
    
    if (needsTos || needsPrivacy) {
      showPolicyDialog.value = true
    }
  } catch (error) {
    console.error('Policy check failed:', error)
    showError('ポリシーの確認に失敗しました。')
  } finally {
    isPolicyCheckPending.value = false
  }
}

const handlePolicyAcceptance = async () => {
  try {
    await store.dispatch('auth/updatePolicyAcceptance', {
      tosAccepted: needsTosAcceptance.value,
      privacyPolicyAccepted: needsPrivacyPolicyAcceptance.value,
    })
    showPolicyDialog.value = false
    needsTosAcceptance.value = false
    needsPrivacyPolicyAcceptance.value = false
    showNotification('ポリシーの同意が更新されました。', 'success')
  } catch (error) {
    console.error('Policy acceptance update failed:', error)
    showError('ポリシーの更新に失敗しました。再度お試しください。')
  }
}

const handlePolicyDisacceptance = async () => {
  try {
    await store.dispatch('auth/signOut')
    showPolicyDialog.value = false
    router.push({ name: 'SignIn' })
  } catch (error) {
    console.error('サインアウトに失敗しました', error)
  }
}

watch(isAuthenticated, (newValue) => {
  if (newValue) {
    checkPolicies()
  } else {
    isPolicyCheckPending.value = false
    showPolicyDialog.value = false
    needsTosAcceptance.value = false
    needsPrivacyPolicyAcceptance.value = false
  }
})

onMounted(() => {
  // 事前ロード
  const img = new Image()
  img.src = new URL('@/assets/images/rakko.webp', import.meta.url).href
  // ローカルストレージからRailModeの状態を読み込む
  const savedRailMode = localStorage.getItem('railMode')
  isRailMode.value = savedRailMode !== null ? JSON.parse(savedRailMode) : true

  checkPolicies()
})

watch(isRailMode, (newValue) => {
  // RailModeの状態が変更されたときにローカルストレージに保存
  localStorage.setItem('railMode', JSON.stringify(newValue))
})
</script>

<style>
#main {
  position: relative;
  background-color: #f1f8fe;
  z-index: 0;
  min-height: 100vh;
}

.wave-container {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 200px;
  overflow: hidden;
  z-index: -1;
}

.wave {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 200%;
  height: 100%;
  background: url('./assets/wave.svg') repeat-x;
  animation: wave 48s cubic-bezier(0.36, 0.45, 0.63, 0.53) infinite;
  transform: translate3d(0, 0, 0);
  will-change: transform;
}

.wave:nth-of-type(2) {
  animation: wave 30s cubic-bezier(0.36, 0.45, 0.63, 0.53) reverse infinite;
  opacity: 0.7;
  z-index: -3;
}

@keyframes wave {
  0% {
    transform: translateX(-5%);
  }
  50% {
    transform: translateX(-30%);
  }
  100% {
    transform: translateX(-5%);
  }
}

.on-wave {
  position: fixed;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  transition: margin-left 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  width: 100%;
  animation: float 16s ease-in-out infinite;
  z-index: -2;
}

@keyframes float {
  0%,
  100% {
    transform: translateX(-50%) translateY(-0px);
  }
  25% {
    transform: translateX(-49%) translateY(-25px);
  }
  50% {
    transform: translateX(-50%) translateY(-10px);
  }
  75% {
    transform: translateX(-51%) translateY(-35px);
  }
}

.custom-snackbar .v-snackbar__wrapper {
  border-radius: 8px !important;
}

.custom-snackbar .v-snackbar__content {
  border-radius: 8px !important;
}
</style>

<style scoped>
.v-application#main {
  max-width: 100%;
  margin: 0 auto;
}

.content-wrapper {
  max-width: 960px;
  margin: 0 auto;
  padding: 0 16px;
}

.navigation-drawer {
  z-index: 1000;
  transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

#main .v-main.noshift {
  padding-left: 56px !important;
}

@media (max-width: 600px) {
  .content-wrapper {
    max-width: 100%;
    padding: 4px;
  }

  .v-container {
    padding: 8px;
  }
}
</style>