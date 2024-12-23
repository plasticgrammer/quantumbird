<template>
  <BaseWidget
    widget-id="organization"
    title="組織情報"
    icon="mdi-domain"
  >
    <v-container class="pa-0 d-flex flex-column" style="height: 100%">
      <div class="flex-grow-1">
        <p class="text-body-1 mb-2">
          {{ organization?.name }}
        </p>
        <p class="text-body-2 mb-1">
          メンバー: {{ memberCount }} 人
        </p>
      </div>
      <div>
        <v-btn
          color="black" variant="outlined"
          :to="{ name: 'OrganizationManagement' }"
          aria-label="組織情報管理ページへ移動"
        >
          <v-icon class="mr-1" small aria-hidden="true">
            mdi-domain
          </v-icon>
          組織情報管理
        </v-btn>
      </div>
    </v-container>
  </BaseWidget>
</template>

<script setup>
import { computed } from 'vue'
import BaseWidget from './BaseWidget.vue'

const props = defineProps({
  organization: {
    type: Object,
    required: true
  },
  members: {
    type: Array,
    required: true
  }
})

const memberCount = computed(() => props.members.length)
</script>