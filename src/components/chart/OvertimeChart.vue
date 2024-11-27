<template>
  <LineChart :chart-data="chartData" :options="chartOptions" />
</template>

<script setup>
import { computed } from 'vue'
import LineChart from './LineChart.vue'

const props = defineProps({
  chartData: {
    type: Object,
    required: true,
    default: () => ({
      labels: [],
      datasets: []
    })
  },
  yAxisTitle: {
    type: String,
    default: '残業時間'
  }
})

const chartOptions = computed(() => ({
  scales: {
    y: {
      min: 0,
      max: getMaxValue(props.chartData.datasets || []),
      ticks: {
        stepSize: Math.ceil(getMaxValue(props.chartData.datasets || []) / 5)
      },
      title: {
        display: true,
        text: props.yAxisTitle
      }
    }
  }
}))

function getMaxValue(datasets) {
  if (!datasets.length) return 3.0
  const allValues = datasets.flatMap(d => d.data)
  return Math.max(...allValues.filter(v => typeof v === 'number'), 3.0)
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
