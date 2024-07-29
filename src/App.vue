<template>
  <v-app id="main">
    <v-navigation-drawer
      v-model="drawer"
      expand-on-hover
      :rail="true"
      permanent
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

    <v-main>
      <router-view />
    </v-main>

    <div v-show="showConfirmDialog">
      <ConfirmationDialog ref="confirmDialog" />
    </div>
  </v-app>
</template>

<script setup>
import { ref, provide } from 'vue'
import { useRouter } from 'vue-router'
import ConfirmationDialog from './components/ConfirmationDialog.vue'

const router = useRouter()
const confirmDialog = ref(null)
const drawer = ref(true)
const showConfirmDialog = ref(false)

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
    icon: 'mdi-account-multiple', 
    title: '週次報告レビュー', 
    value: 'WeeklyReview', 
    route: { name: 'WeeklyReviewSelector' }
  },
]

const navigateTo = (route, params = {}) => {
  router.push({ ...route, params: { ...route.params, ...params } })
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
</script>

<style scoped>
.v-application#main {
  max-width: 960px;
  margin: 0 auto;
}
</style>