<template>
  <v-app id="main">
    <template v-if="!$route.meta.hideAnimation">
      <div v-for="i in 2" :key="i" class="wave"></div>
      <v-img
        src="@/assets/images/rakko.png"
        max-width="40%"
        width="340"
        class="on-wave mx-auto"
        :style="bgImageStyle"
      ></v-img>
    </template>

    <v-snackbar
      v-model="notification.show"
      :color="notification.type"
      :timeout="5000"
      location="top"
      width="90%"
      class="mx-auto"
    >
      <div class="d-flex align-center py-1">
        <v-icon
          :icon="getNotificationIcon"
          class="mr-2"
          color="white"
        />
        {{ notification.message }}
      </div>
      <template #actions>
        <v-btn
          color="white"
          variant="text"
          icon="mdi-close"
          @click="closeNotification"
        >
        </v-btn>
      </template>
    </v-snackbar>

    <template v-if="!$route.meta.hideNavigation">
      <v-navigation-drawer
        v-if="!isMobile"
        v-model="drawer"
        :rail="isRailModeActive"
        permanent
        location="left"
        :width="235"
        color="blue-grey-darken-2"
        class="navigation-drawer d-print-none"
        @mouseenter="isHovered = true"
        @mouseleave="isHovered = false"
      >
        <v-list>
          <v-list-item class="dense-list-item pr-2">
            <template #prepend>
              <v-icon 
                v-ripple
                icon="mdi-menu"
                class="opacity-100 mr-1"
                @click="toggleDrawerMode"
              ></v-icon>
            </template>
            <v-list-item-title>
              <v-img
                src="@/assets/logo.png"
                class="cursor-pointer"
                @click="navigateTo({ name: 'Overview' })"
              ></v-img>
            </v-list-item-title>
            <template #append>
              <v-icon 
                :icon="isRailMode ? 'mdi-format-horizontal-align-right' : 'mdi-format-horizontal-align-left'"
                @click="toggleDrawerMode"
              ></v-icon>
            </template>
          </v-list-item>
        </v-list>
        <v-divider></v-divider>
        <v-list nav>
          <v-list-item
            v-for="item in navigationItems"
            :key="item.value"
            :prepend-icon="item.icon"
            :title="item.title"
            :value="item.value"
            @click="navigateTo(item.route)"
          />
        </v-list>

        <template #append>
          <v-divider />
          <div class="dropdown-container">
            <v-list>
              <v-list-item
                :title="user.email"
                :subtitle="user.organizationId"
                class="dense-list-item"
              >
                <template #prepend>
                  <v-avatar>
                    <v-icon icon="mdi-account-circle"></v-icon>
                  </v-avatar>
                </template>
                <template #append>
                  <v-btn
                    :icon="showDropdown ? 'mdi-menu-up' : 'mdi-menu-down'"
                    class="mr-n2"
                    size="x-small"
                    variant="text"
                  ></v-btn>
                </template>
              </v-list-item>
            </v-list>
            <v-menu
              v-model="showDropdown"
              activator="parent"
              location="top"
            >
              <v-list class="pa-0 bg-blue-grey-darken-1">
                <v-list-item>
                  <v-list-item-title class="text-body-2 opacity-60">{{ user.email }}</v-list-item-title>
                </v-list-item>
                <v-divider></v-divider>
                <v-list-item @click="handleSignOut">
                  <template #prepend>
                    <v-icon icon="mdi-logout-variant"></v-icon>
                  </template>
                  <v-list-item-title>サインアウト</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
          </div>
        </template>
      </v-navigation-drawer>

      <v-bottom-navigation
        v-else
        bg-color="blue-grey-darken-2"
        class="d-print-none"
        grow
      >
        <v-btn
          v-for="item in navigationItems"
          :key="item.value"
          :value="item.value"
          @click="navigateTo(item.route)"
        >
          <v-icon size="x-large">
            {{ item.icon }}
          </v-icon>
        </v-btn>
      </v-bottom-navigation>
    </template>

    <v-main :class="{ 'noshift': isRailModeActive }" :style="appStyle">
      <div class="content-wrapper">
        <router-view />
      </div>
    </v-main>

    <ConfirmationDialog v-if="showConfirmDialog" ref="confirmDialog" />
  </v-app>
</template>

<script setup>
import { ref, provide, reactive, computed, watch, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { useResponsive } from './composables/useResponsive'
import ConfirmationDialog from './components/ConfirmationDialog.vue'

const { isMobile } = useResponsive()

const store = useStore()
const router = useRouter()
const confirmDialog = ref(null)
const drawer = ref(true)
const isRailMode = ref(true)
const isHovered = ref(false)
const showConfirmDialog = ref(false)
const showDropdown = ref(false)

const user = computed(() => ({
  organizationId: store.getters['auth/organizationId'],
  username: store.getters['auth/name'],
  email: store.getters['auth/email']
}))

const isRailModeActive = computed(() => !isMobile.value && isRailMode.value && !isHovered.value && !showDropdown.value)

const appStyle = computed(() => ({
  paddingBottom: (router.currentRoute.value.meta.hideAnimation ? 30 : 260) + 'px'
}))

const bgImageStyle = computed(() => ({
  marginLeft: (isMobile.value ? 0 : (isRailModeActive.value ? 56 : 180)) + 'px !important',
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

const showNotification = (message, type, error = false) => {
  notification.show = true
  notification.type = type || 'success'
  notification.message = message
  if (error) {
    console.error(error)
  }
}

const closeNotification = () => {
  notification.show = false
}

const showConfirmDialogGlobal = async (title, message) => {
  try {
    showConfirmDialog.value = true
    return await confirmDialog.value?.open(title, message)
  } catch (error) {
    console.error('Error showing confirmation dialog:', error)
  } finally {
    showConfirmDialog.value = false
  }
}

provide('showConfirmDialog', showConfirmDialogGlobal)
provide('showNotification', showNotification)

const navigateTo = (route, params = {}) => {
  router.push({ ...route, params: { ...route.params, ...params } })
  if (isMobile.value) {
    drawer.value = false
  }
}

const handleSignOut = async () => {
  try {
    await store.dispatch('auth/signOut')
    router.push({ name: 'SignIn' })
  } catch (error) {
    console.error('Sign out error:', error)
    showNotification('サインアウトに失敗しました', 'error')
  }
}

onMounted(() => {
  // ローカルストレージからRailModeの状態を読み込む
  const savedRailMode = localStorage.getItem('railMode')
  if (savedRailMode !== null) {
    isRailMode.value = JSON.parse(savedRailMode)
  }
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

.wave {
  /* blue-lighten-2 64B5F6 */
  position: fixed;
  bottom: 0;
  left: 0;
  width: 300%;
  height: 200px;
  background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 800 200'%3E%3Cdefs%3E%3ClinearGradient id='waveGradient' x1='0%25' y1='0%25' x2='0%25' y2='100%25'%3E%3Cstop offset='0%25' style='stop-color:%2364B5F6;stop-opacity:0.6' /%3E%3Cstop offset='100%25' style='stop-color:%2364B5F6;stop-opacity:0.78' /%3E%3C/linearGradient%3E%3C/defs%3E%3Cpath d='M0 50c200 0 250 50 400 50 150 0 200-50 400-50v150H0z' fill='url(%23waveGradient)'/%3E%3C/svg%3E");
  animation: wave 96s cubic-bezier(0.36, 0.45, 0.63, 0.53) infinite;
  transform: translate3d(0, 0, 0);
  z-index: -1;
}

.wave:nth-of-type(2) {
  animation: wave 60s cubic-bezier(0.36, 0.45, 0.63, 0.53) reverse infinite;
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
  transition: margin-left 0.2s cubic-bezier(0.4, 0, 0.2, 1);
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
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

#main .v-main.noshift {
  padding-left: 56px !important;
}

@media (max-width: 600px) {
  .content-wrapper {
    max-width: 100%;
    padding: 8px;
  }
}
</style>