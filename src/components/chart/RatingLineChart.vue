<template>
  <div class="rating-chart">
    <canvas ref="chartRef"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import { Chart } from 'chart.js'
import { updateChartInstance } from './chartUtils'

const props = defineProps({
  chartData: {
    type: Object,
    required: true
  }
})

const chartRef = ref(null)
let chartInstance = null

const getMaxOvertimeHours = (datasets) => {
  const overtimeDataset = datasets.find(d => d.yAxisID === 'y1')
  if (!overtimeDataset) return 8
  const maxHours = Math.max(...overtimeDataset.data)
  return Math.max(8, Math.ceil(maxHours / 4) * 4)
}

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom'
    }
  },
  scales: {
    y: {
      type: 'linear',
      position: 'left',
      min: 1,
      max: 5,
      ticks: {
        stepSize: 1,
        precision: 0,
        callback: function(value) {
          return Number.isInteger(value) ? value : ''
        }
      },
      title: {
        display: true,
        text: '評価'
      }
    },
    y1: {
      type: 'linear',
      position: 'right',
      min: 0,
      grid: {
        drawOnChartArea: false
      },
      ticks: {
        stepSize: 2,
        precision: 0,
        callback: function(value) {
          return value + 'h'
        }
      },
      title: {
        display: true,
        text: '残業時間'
      },
      afterDataLimits: (scale) => {
        scale.max = getMaxOvertimeHours(props.chartData.datasets)
      }
    }
  }
}

onMounted(() => {
  if (chartRef.value) {
    chartInstance = new Chart(chartRef.value, {
      type: 'line',
      data: props.chartData,
      options: chartOptions
    })
  }
})

watch(() => props.chartData, (newData) => {
  if (chartInstance && newData) {
    updateChartInstance({
      chart: chartInstance,
      chartData: newData,
      isTop3: false,
      options: chartOptions
    })
  }
}, { deep: true })

onBeforeUnmount(() => {
  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }
})
</script>

<style scoped>
.rating-chart {
  height: 240px;
  position: relative;
  width: 100%;
}
</style>
