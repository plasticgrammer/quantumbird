
<template>
  <BaseWidget
    :widget-id="widgetId"
    :title="title"
    icon="mdi-chart-line"
    content-class="pb-1"
  >
    <Suspense v-if="isDataReady">
      <template #default>
        <component :is="chartComponent" :chart-data="chartData" />
      </template>
      <template #fallback>
        <div aria-live="polite">読み込み中...</div>
      </template>
    </Suspense>
    <div v-else aria-live="polite">準備中...</div>
  </BaseWidget>
</template>

<script setup>
import BaseWidget from './BaseWidget.vue'

defineProps({
  widgetId: { type: String, required: true },
  title: { type: String, required: true },
  chartComponent: { type: Object, required: true },
  chartData: { type: Object, required: true },
  isDataReady: { type: Boolean, required: true }
})
</script>