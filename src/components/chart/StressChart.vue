<template>
  <canvas ref="chartRef"></canvas>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
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

const initChart = () => {
  if (chartRef.value && props.chartData) {
    const ctx = chartRef.value.getContext('2d')
    chartInstance = new Chart(ctx, {
      type: 'line',
      data: props.chartData,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
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
              callback: function(value) {
                if (value === 1) return '低'
                if (value === 5) return '高'
                return value.toString()
              }
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
}

onMounted(() => {
  if (props.chartData) {
    initChart()
  }
})

watch(() => props.chartData, () => {
  if (chartInstance) {
    chartInstance.destroy()
  }
  initChart()
}, { deep: true })
</script>