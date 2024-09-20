<template>
  <canvas ref="chartRef" class="chart-canvas"></canvas>
</template>

<script setup>
import { watch, nextTick, computed } from 'vue'
import { useChart } from './chartUtils'

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

// データの最大値を計算
const maxDataValue = computed(() => {
  if (!props.chartData.datasets || props.chartData.datasets.length === 0) {
    return 3.0 // デフォルト値
  }
  const allValues = props.chartData.datasets.flatMap(dataset => dataset.data)
  return Math.max(...allValues, 3.0)
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
      beginAtZero: true,
      title: {
        display: true,
        text: props.yAxisTitle
      },
      max: maxDataValue.value,
      ticks: {
        stepSize: Math.ceil(maxDataValue.value / 5)
      }
    }
  }
})

const { chartRef, initChart, updateChart } = useChart('line', createChartOptions)

watch([() => props.chartData, () => props.yAxisTitle], ([newData, newTitle], [oldData, oldTitle]) => {
  if (JSON.stringify(newData) !== JSON.stringify(oldData) || newTitle !== oldTitle) {
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