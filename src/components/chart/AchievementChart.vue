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
      if (value === 1) return '課題あり'
      if (value === 5) return '理想以上'
      return ''
    },
    includeBounds: false
  },
  title: {
    display: true,
    text: 'タスク達成度'
  },
  grid: {
    color: (context) => context.tick.value === 5 ? 'rgba(0, 0, 0, 0.2)' : 'rgba(0, 0, 0, 0.1)'
  }
}
</script>