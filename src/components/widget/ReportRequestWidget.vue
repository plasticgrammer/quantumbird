<template>
  <BaseWidget
    widget-id="reportRequest"
    title="報告依頼"
    icon="mdi-mail"
  >
    <v-container class="pa-0 d-flex flex-column" style="height: 100%">
      <div class="flex-grow-1">
        <p class="text-body-2 mb-1">
          <span>自動報告依頼設定: </span>
          <v-icon
            :color="organization.requestEnabled ? 'success' : 'grey'"
            class="mx-1"
            aria-hidden="true"
          >
            {{ organization.requestEnabled ? 'mdi-timer-outline' : 'mdi-timer-off-outline' }}
          </v-icon>
          <span class="text-subtitle-1">
            <strong>{{ organization.requestEnabled ? '有効' : '無効' }}</strong>
          </span>
        </p>
        <p v-if="organization.requestEnabled && nextRequestDateTime" class="text-body-2 mb-1">
          <span class="mr-2">次回報告依頼日時: </span>
          <span class="text-subtitle-1">{{ nextRequestDateTimeString }}</span>
        </p>
      </div>
      <div>
        <v-btn
          color="black" variant="outlined"
          :to="{ name: 'RequestSetting' }"
          aria-label="報告依頼設定ページへ移動"
        >
          <v-icon class="mr-1" small aria-hidden="true">
            mdi-mail
          </v-icon>
          報告依頼設定
        </v-btn>
      </div>
    </v-container>
  </BaseWidget>
</template>

<script setup>
import BaseWidget from './BaseWidget.vue'

defineProps({
  organization: {
    type: Object,
    required: true
  },
  nextRequestDateTime: {
    type: Date,
    default: null
  },
  nextRequestDateTimeString: {
    type: String,
    default: ''
  }
})
</script>