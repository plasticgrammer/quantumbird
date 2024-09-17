<template>
  <v-dialog
    v-model="isOpen"
    max-width="400px"
  >
    <v-card>
      <v-card-title class="bg-primary">
        {{ currentTitle }}
      </v-card-title>
      <v-card-text>
        <pre class="message-text">{{ currentMessage }}</pre>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn
          color="grey darken-1"
          text
          @click="cancel"
        >
          キャンセル
        </v-btn>
        <v-btn
          color="primary"
          @click="confirm"
        >
          実行
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref } from 'vue'

const isOpen = ref(false)
const currentTitle = ref('')
const currentMessage = ref('')
let resolvePromise = null

const open = (title = '確認', message) => {
  currentTitle.value = title
  currentMessage.value = message
  isOpen.value = true
  return new Promise((resolve) => {
    resolvePromise = resolve
  })
}

const cancel = () => {
  isOpen.value = false
  resolvePromise(false)
}

const confirm = () => {
  isOpen.value = false
  resolvePromise(true)
}

defineExpose({ open })
</script>

<style scoped>
.message-text {
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: inherit;
  font-size: inherit;
  line-height: 1.5;
  margin: 0;
  padding: 0;
}
</style>