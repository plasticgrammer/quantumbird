<template>
  <v-app id="main">
    <v-navigation-drawer
      color="secondary"
      expand-on-hover
      rail
    >
      <v-list>
        <v-list-item
          prepend-icon="mdi-bird"
          subtitle="plasticgrammer@gmailcom"
          title="plasticgrammer"
        />
      </v-list>

      <v-divider />

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
        <div class="pa-2">
          <v-btn block />
        </div>
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
import { ref, provide, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import ConfirmationDialog from './components/ConfirmationDialog.vue'

const router = useRouter()
const confirmDialog = ref(null)
const drawer = ref(false)
const showConfirmDialog = ref(false)

const navigationItems = [
  { 
    icon: 'mdi-view-dashboard', 
    title: 'Dashboard', 
    value: 'Dashboard', 
    route: { name: 'Dashboard' }
  },
  { 
    icon: 'mdi-domain', 
    title: 'Organization', 
    value: 'Organization', 
    route: { name: 'OrganizationManagement' }
  },
  { 
    icon: 'mdi-account-multiple', 
    title: 'WeeklyReview', 
    value: 'WeeklyReview', 
    route: { name: 'WeeklyReviewSelector' }
  },
]

const navigateTo = (route, params = {}) => {
  router.push({ ...route, params: { ...route.params, ...params } })
  drawer.value = false
}

const showConfirmDialogGlobal = async (title, message) => {
  try {
    showConfirmDialog.value = true
    return await confirmDialog.value?.open(title, message)
  } catch (error) {
    console.error('Error showing confirmation dialog:', error)
    // エラー時の適切な処理を追加
  } finally {
    showConfirmDialog.value = false
  }
}

// 確認ダイアログ関数を子コンポーネントに提供
provide('showConfirmDialog', showConfirmDialogGlobal)

// ローカルストレージからドロワーの状態を復元
onMounted(() => {
  const savedDrawerState = localStorage.getItem('app-drawer-state')
  if (savedDrawerState !== null) {
    drawer.value = savedDrawerState === 'true'
  }
})

// ドロワーの状態が変更されたときにローカルストレージに保存
watch(drawer, (newValue) => {
  localStorage.setItem('app-drawer-state', String(newValue))
})
</script>

<style scoped>
.v-application#main {
  max-width: 960px;
  margin: 0 auto;
}
</style>