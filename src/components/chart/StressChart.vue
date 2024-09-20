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
      min: 0.8, // 1よりも少し下に設定
      max: 5.2, // 5よりも少し上に設定
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