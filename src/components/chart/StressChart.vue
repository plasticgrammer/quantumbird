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
      if (value === 1) return '余裕'
      if (value === 5) return '極限'
      return ''
    },
    includeBounds: false
  },
  title: {
    display: true,
    text: 'ストレス評価'
  },
  grid: {
    color: (context) => context.tick.value === 5 ? 'rgba(0, 0, 0, 0.2)' : 'rgba(0, 0, 0, 0.1)'
  }
}
</script>

<style scoped>
.chart-container {
  width: 100%;
}

.chart-wrapper {
  position: relative;
  height: 180px;
  width: 100%;
}

.chart-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100% !important;
  height: 100% !important;
}
</style>