<template>
  <BaseWidget
    widget-id="weeklyReport"
    title="メンバーの週次報告"
    icon="mdi-calendar-account"
  >
    <v-container class="pa-0 d-flex flex-column" style="height: 100%">
      <div class="flex-grow-1">
        <v-select
          v-model="selectedMember"
          :items="members"
          item-title="name"
          item-value="memberUuid"
          label="メンバー選択"
          density="comfortable"
          variant="outlined"
          hide-details
          prepend-inner-icon="mdi-account"
        ></v-select>
      </div>
      <div>
        <v-btn
          color="black"
          variant="outlined"
          :disabled="!selectedMember"
          x-small
          aria-label="選択したメンバーの週次報告ページを新しいタブで開く"
          @click="navigateToReport"
        >
          週次報告（代理入力）
          <v-icon icon="mdi-open-in-new" end small aria-hidden="true" />
        </v-btn>
      </div>
    </v-container>
  </BaseWidget>
</template>

<script setup>
import { ref } from 'vue'
import { rootUrl } from '@/config/environment'
import BaseWidget from './BaseWidget.vue'

const props = defineProps({
  members: {
    type: Array,
    required: true
  },
  weekString: {
    type: String,
    required: true
  },
  organizationId: {
    type: String,
    required: true
  }
})

const selectedMember = ref(null)

const navigateToReport = () => {
  if (!selectedMember.value) return
  
  const baseUrl = `${rootUrl}/reports/${props.organizationId}/${selectedMember.value}`
  const url = props.weekString ? `${baseUrl}/${props.weekString}` : baseUrl
  
  window.open(url, '_blank', 'noopener,noreferrer')
}
</script>