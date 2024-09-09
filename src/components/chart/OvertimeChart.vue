<template>
  <canvas ref="chartRef" class="chart-canvas"></canvas>
</template>

<script setup>
import { ref, onMounted, watch, nextTick, computed } from 'vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

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

const chartRef = ref(null)
let chartInstance = null

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

const createChart = () => {
  const ctx = chartRef.value.getContext('2d')
  return new Chart(ctx, {
    type: 'line',
    data: props.chartData,
    options: createChartOptions()
  })
}

const initChart = () => {
  if (chartRef.value && props.chartData) {
    try {
      chartInstance = createChart()
    } catch (error) {
      console.error('Failed to create chart:', error)
    }
  }
}

const updateChart = () => {
  if (chartInstance) {
    chartInstance.data = props.chartData
    chartInstance.options = createChartOptions()
    chartInstance.update()
  } else {
    initChart()
  }
}

onMounted(() => {
  if (props.chartData) {
    nextTick(initChart)
  }
})

watch([() => props.chartData, () => props.yAxisTitle], ([newData, newTitle], [oldData, oldTitle]) => {
  if (JSON.stringify(newData) !== JSON.stringify(oldData) || newTitle !== oldTitle) {
    nextTick(updateChart)
  }
}, { deep: true })
</script>

<style scoped>
canvas {
  width: 100% !important;
  height: 100% !important;
}
</style>