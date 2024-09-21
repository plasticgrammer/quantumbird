<template>
  <canvas ref="chartRef" class="chart-canvas"></canvas>
</template>

<script setup>
import { ref, watch, nextTick, computed, onMounted, onUnmounted } from 'vue'
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

const chartInstance = ref(null)
const isMounted = ref(false)

const { chartRef, createChart, updateChart } = useChart('line', createChartOptions)

const initChart = (data) => {
  if (isMounted.value && chartRef.value) {
    chartInstance.value = createChart(data)
  }
}

const updateChartData = (data) => {
  if (isMounted.value && chartInstance.value) {
    updateChart(chartInstance.value, data)
  }
}

watch(() => props.chartData, (newData, oldData) => {
  if (JSON.stringify(newData) !== JSON.stringify(oldData)) {
    nextTick(() => updateChartData(newData))
  }
}, { deep: true })

watch(() => props.yAxisTitle, (newTitle, oldTitle) => {
  if (newTitle !== oldTitle) {
    nextTick(() => {
      if (chartInstance.value) {
        chartInstance.value.options.scales.y.title.text = newTitle
        chartInstance.value.update()
      }
    })
  }
})

onMounted(() => {
  isMounted.value = true
  nextTick(() => initChart(props.chartData))
})

onUnmounted(() => {
  isMounted.value = false
  if (chartInstance.value) {
    chartInstance.value.destroy()
  }
})
</script>

<style scoped>
canvas {
  width: 100% !important;
  height: 100% !important;
}
</style>