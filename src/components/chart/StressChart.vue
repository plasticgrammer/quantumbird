<template>
  <canvas ref="chartRef"></canvas>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
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
  }
})

const chartRef = ref(null)
let chartInstance = null

const createChart = () => {
  const ctx = chartRef.value.getContext('2d')
  return new Chart(ctx, {
    type: 'line',
    data: props.chartData,
    options: {
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
            callback: (value) => value === 1 ? '低' : value === 5 ? '高' : ''
          },
          title: {
            display: true,
            text: 'ストレス評価'
          }
        }
      }
    }
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

watch(() => props.chartData, (newData, oldData) => {
  if (JSON.stringify(newData) !== JSON.stringify(oldData)) {
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