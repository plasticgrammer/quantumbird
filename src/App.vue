<template>
  <v-app id="main">
    <v-app-bar
      color="secondary"
      :elevation="2"
      scroll-behavior="hide"
    >
      <v-app-bar-nav-icon
        aria-label="Toggle navigation menu"
        @click.stop="toggleDrawer"
      />
      
      <v-app-bar-title>SixWeeks</v-app-bar-title>
    </v-app-bar>

    <v-navigation-drawer
      v-model="drawer"
      :location="$vuetify.display.mobile ? 'bottom' : 'left'"
      temporary
    >
      <v-list>
        <v-list-item
          v-for="item in items"
          :key="item.value"
          :value="item.value"
          :title="item.title"
          @click="handleNavigation(item)"
        />
      </v-list>
    </v-navigation-drawer>

    <v-main>
      <router-view />
    </v-main>

    <ConfirmationDialog
      v-show="showConfirmDialog"
      ref="confirmDialog"
    />
  </v-app>
</template>

<script setup>
import { ref, provide, onMounted, watch } from 'vue'
import ConfirmationDialog from './components/ConfirmationDialog.vue'

const confirmDialog = ref(null)
const drawer = ref(false)
const showConfirmDialog = ref(false)

const items = ref([
  { title: 'Foo', value: 'foo' },
  { title: 'Bar', value: 'bar' },
  { title: 'Fizz', value: 'fizz' },
  { title: 'Buzz', value: 'buzz' },
])

const toggleDrawer = () => {
  drawer.value = !drawer.value
  localStorage.setItem('app-drawer-state', String(drawer.value))
}

const handleNavigation = (item) => {
  // ナビゲーション処理をここに実装
  console.log(`Navigating to ${item.value}`)
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