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
        permanent
        location="left"
        :temporary="isMobile"
        expand-on-hover
        rail
        color="secondary d-print-none"
      >
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
          <v-list>
            <v-list-item
              :title="user.username"
              :subtitle="user.email"
            >
              <template #prepend>
                <v-avatar color="secondary">
                  <v-icon icon="mdi-account-circle"></v-icon>
                </v-avatar>
              </template>
            </v-list-item>
          </v-list>
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

    <v-main>
      <router-view />
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
import { useResponsive } from './composables/useResponsive'
import ConfirmationDialog from './components/ConfirmationDialog.vue'

const { isMobile } = useResponsive()

const store = useStore()
const router = useRouter()
const confirmDialog = ref(null)
const drawer = ref(true)
const showConfirmDialog = ref(false)
const user = ref({
  username: store.getters['user/organizationId'],
  email: store.getters['user/email']
})

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

<style scoped>
.v-application#main {
  max-width: 960px;
  margin: 0 auto;
}

@media (max-width: 600px) {
  .v-application#main {
    max-width: 100%;
  }
}
</style>