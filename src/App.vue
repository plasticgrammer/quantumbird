<template>
  <v-app id="main">
    <v-snackbar
      v-model="notification.show"
      :color="notification.type"
      :timeout="5000"
      location="top"
    >
      {{ notification.message }}
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

    <v-app-bar v-if="isMobile" color="secondary" app>
      <v-app-bar-nav-icon @click="drawer = !drawer"></v-app-bar-nav-icon>
      <v-toolbar-title>週次報告システム</v-toolbar-title>
    </v-app-bar>

    <template v-if="!$route.meta.hideNavigation">
      <v-navigation-drawer
        v-model="drawer"
        permanent
        :location="drawerLocation"
        :temporary="isMobile"
        :expand-on-hover="!isMobile"
        :rail="!isMobile"
        color="secondary"
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
import { useRouter } from 'vue-router'
import ConfirmationDialog from './components/ConfirmationDialog.vue'
import { useResponsive } from './composables/useResponsive'

const router = useRouter()
const confirmDialog = ref(null)
const drawer = ref(true)
const showConfirmDialog = ref(false)

const { isMobile } = useResponsive()
const drawerLocation = computed(() => isMobile.value ? 'bottom' : 'left')

const user = ref({
  username: 'plasticgrammer',
  email: 'plasticgrammer@gmail.com'
})

const navigationItems = [
  { 
    icon: 'mdi-view-dashboard', 
    title: 'ダッシュボード', 
    value: 'Dashboard', 
    route: { name: 'Dashboard' }
  },
  { 
    icon: 'mdi-domain', 
    title: '組織情報管理', 
    value: 'Organization', 
    route: { name: 'OrganizationManagement' }
  },
  { 
    icon: 'mdi-calendar-multiple-check', 
    title: '週次報告レビュー', 
    value: 'WeeklyReview', 
    route: { name: 'WeeklyReviewSelector' }
  },
]

const notification = reactive({
  show: false,
  type: 'success',
  message: ''
})

const showNotification = (message, error = false) => {
  notification.show = true
  notification.type = error ? 'error' : 'success'
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