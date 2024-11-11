<template>
  <v-overlay 
    :model-value="isLoading" 
    class="opacity-50 align-center justify-center"
    persistent
  >
    <v-progress-circular size="70" width="13" color="primary" indeterminate></v-progress-circular>
  </v-overlay>
</template>

<script setup>
import { computed } from 'vue'
import { useStore } from 'vuex'

const store = useStore()
const isLoading = computed(() => store.getters.isLoading)
</script>