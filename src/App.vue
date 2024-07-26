<template>
  <v-app id="main">
    <v-main>
      <router-view />
    </v-main>
    <ConfirmationDialog ref="confirmDialog" />
  </v-app>
</template>

<script setup>
import { ref, provide } from 'vue'
import ConfirmationDialog from './components/ConfirmationDialog.vue'

const confirmDialog = ref(null)

// グローバルな確認ダイアログ関数を提供
const showConfirmDialog = (title, message) => {
  return confirmDialog.value.open(title, message)
}

// 確認ダイアログ関数を子コンポーネントに提供
provide('showConfirmDialog', showConfirmDialog)
</script>

<style scoped>
#main {
  max-width: 960px;
  margin: 0 auto;
}
</style>