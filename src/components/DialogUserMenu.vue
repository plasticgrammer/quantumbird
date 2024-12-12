<template>
  <v-dialog v-model="dialog" fullscreen>
    <v-card>
      <v-toolbar color="menu">
        <v-btn icon @click="closeDialog">
          <v-icon>mdi-close</v-icon>
        </v-btn>
        <v-toolbar-title>メニュー</v-toolbar-title>
      </v-toolbar>

      <UserMenu
        :model-value="dialog"
        bg-color="menu"
        mobile
        wrapper="div"
        @close="closeDialog"
        @sign-out="handleSignOut"
      />
    </v-card>
  </v-dialog>
</template>

<script setup>
import { computed } from 'vue'
import UserMenu from './UserMenu.vue'

const props = defineProps({
  modelValue: Boolean
})

const emit = defineEmits(['update:modelValue', 'sign-out'])

const dialog = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const closeDialog = () => {
  dialog.value = false
}

const handleSignOut = () => {
  closeDialog()
  emit('sign-out')
}
</script>