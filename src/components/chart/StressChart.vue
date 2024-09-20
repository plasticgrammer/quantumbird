<template>
  <canvas ref="chartRef" class="chart-canvas"></canvas>
</template>

<script setup>
import { watch, nextTick } from 'vue'
import { useChart } from './chartUtils'

const props = defineProps({
  chartData: {
    type: Object,
    required: true,
    default: () => ({
      labels: [],
      datasets: []
    })
  }
})

const createChartOptions = () => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom',
    },
    title: {
      display: false
    }
  },
  scales: {
    y: {
      beginAtZero: false,
      min: 1,
      max: 5,
      ticks: {
        stepSize: 1,
        precision: 0,
        callback: (value) => value === 1 ? '余裕' : value === 5 ? '極限' : ''
      },
      title: {
        display: true,
        text: 'ストレス評価'
      }
    }
  }
})

const { chartRef, initChart, updateChart } = useChart('line', createChartOptions)

watch(() => props.chartData, (newData, oldData) => {
  if (JSON.stringify(newData) !== JSON.stringify(oldData)) {
    nextTick(() => updateChart(props.chartData))
  }
}, { deep: true })

nextTick(() => initChart(props.chartData))
</script>

<style scoped>
canvas {
  width: 100% !important;
  height: 100% !important;
}
</style>