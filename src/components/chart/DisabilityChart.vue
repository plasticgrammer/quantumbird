<template>
  <BaseChart
    :widget-id="widgetId"
    :title="title"
    :chart-data="chartData"
    :y-axis-config="yAxisConfig"
  />
</template>

<script setup>
import BaseChart from './BaseChart.vue'

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

const yAxisConfig = {
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
</script>