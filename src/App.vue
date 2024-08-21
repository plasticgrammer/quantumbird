<template>
  <v-app id="main">
    <v-snackbar
      v-model="notification.show"
      :color="notification.type"
      :timeout="5000"
      location="top"
    >
      <div class="d-flex align-center">
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
        :rail="isRailMode && !isHovered && !showDropdown"
        permanent
        location="left"
        :width="235"
        color="teal-lighten-2"
        class="navigation-drawer d-print-none"
        @mouseleave="onDrawerLeave"
      >
        <v-list>
          <v-list-item
            class="logo-list-item pr-2"
            @mouseenter="onDrawerEnter"
          >
            <template #prepend>
              <v-icon 
                v-ripple
                icon="mdi-menu"
                color="white" 
                class="opacity-100 mr-3"
                @click="toggleDrawerMode"
              ></v-icon>
            </template>
            <v-list-item-title>
              <v-img
                src="@/assets/logo.png"
              ></v-img>
            </v-list-item-title>
            <v-list-item-subtitle class="pl-1">{{ user.organizationId }}</v-list-item-subtitle>
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
          <div class="dropdown-container" @mouseenter="onDrawerEnter">
            <v-list>
              <v-list-item
                :title="user.username"
                :subtitle="user.email"
              >
                <template #prepend>
                  <v-avatar color="teal-lighten-2">
                    <v-icon icon="mdi-account-circle"></v-icon>
                  </v-avatar>
                </template>
                <template #append>
                  <v-btn
                    :icon="showDropdown ? 'mdi-menu-up' : 'mdi-menu-down'"
                    size="small"
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
              <v-list class="custom-dropdown bg-teal-lighten-2">
                <v-list-item>
                  <v-list-item-title class="text-body-2 opacity-80">{{ user.email }}</v-list-item-title>
                </v-list-item>
                <v-divider></v-divider>
                <v-list-item @click="handleSignOut">
                  <v-list-item-title>サインアウト</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
          </div>
        </template>
      </v-navigation-drawer>

      <v-bottom-navigation
        v-else
        bg-color="blue-grey-darken-3"
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

    <v-main :class="{ 'noshift': isHovered || showDropdown }">
      <div class="content-wrapper">
        <router-view />
      </div>
    </v-main>

    <div v-show="showConfirmDialog">
      <ConfirmationDialog ref="confirmDialog" />
    </div>
  </v-app>
</template>

<script setup>
import { ref, provide, reactive, computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { signOut } from '@aws-amplify/auth'
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

const user = ref({
  organizationId: store.getters['user/organizationId'],
  username: store.getters['user/name'],
  email: store.getters['user/email']
})

const toggleDrawerMode = () => {
  isRailMode.value = !isRailMode.value
  isHovered.value = false
}

const onDrawerEnter = () => {
  if (isRailMode.value) {
    isHovered.value = true
  }
}

const onDrawerLeave = () => {
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
  case 'success':
    return 'mdi-check-circle'
  case 'error':
    return 'mdi-alert-circle'
  case 'warning':
    return 'mdi-alert'
  case 'info':
    return 'mdi-information'
  default:
    return 'mdi-bell'
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

const navigateTo = (route, params = {}) => {
  router.push({ ...route, params: { ...route.params, ...params } })
  if (isMobile.value) {
    drawer.value = false
  }
}

const handleSignOut = async () => {
  try {
    await signOut()
    router.push({ name: 'SignIn' })
  } catch (error) {
    console.error('Sign out error:', error)
    showNotification('サインアウトに失敗しました', 'error')
  }
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
</script>

<style>
.logo-list-item .v-list-item__spacer {
  width: 8px !important;
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
  transition: width 0.3s ease;
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

.custom-dropdown {
  min-width: 200px;
}
</style>