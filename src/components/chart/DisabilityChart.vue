<template>
  <BaseWidget
    :widget-id="widgetId"
    :title="title"
    icon="mdi-chart-line"
  >
    <LineChart :chart-data="chartData" :options="chartOptions" />
  </BaseWidget>
</template>

<script setup>
import { computed } from 'vue'
import BaseWidget from '../widget/BaseWidget.vue'
import LineChart from './LineChart.vue'

defineProps({
  widgetId: {
    type: String,
    required: true
  },
  title: {
    type: String,
    required: true
  },
  chartData: {
    type: Object,
    required: true,
    default: () => ({
      labels: [],
      datasets: []
    })
  }
})

const chartOptions = computed(() => ({
  yAxis: {
    min: 0.8,
    max: 5.2,
    ticks: {
      stepSize: 1,
      precision: 0,
      callback: (value) => {
        if (value === 1) return '易しい'
        if (value === 5) return '難しい'
        return ''
      },
      includeBounds: false
    },
    title: {
      display: true,
      text: 'タスク難易度'
    },
    grid: {
      color: (context) => context.tick.value === 5 ? 'rgba(0, 0, 0, 0.2)' : 'rgba(0, 0, 0, 0.1)'
    }
  }
}))
</script>