<template>
  <canvas ref="chartRef" class="chart-canvas"></canvas>
</template>

<script setup>
import { ref, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { useChart } from './chartUtils'

const props = defineProps({
  chartData: {
    type: Object,
    required: true,
    validator: (value) => {
      return value && Array.isArray(value.labels) && Array.isArray(value.datasets)
    }
  }
})

const emit = defineEmits(['error'])

const isMounted = ref(false)
const chartInstance = ref(null)

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
      min: 0.8,
      max: 5.2,
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

const { chartRef, createChart, updateChart } = useChart('line', createChartOptions)

const initChart = (data) => {
  if (isMounted.value && chartRef.value) {
    try {
      chartInstance.value = createChart(data)
    } catch (error) {
      console.error('Error initializing chart:', error)
      emit('error', error)
    }
  }
}

const updateChartData = (data) => {
  if (isMounted.value && chartInstance.value) {
    try {
      updateChart(chartInstance.value, data)
    } catch (error) {
      console.error('Error updating chart:', error)
      emit('error', error)
    }
  }
}

watch(() => props.chartData, (newData, oldData) => {
  if (JSON.stringify(newData) !== JSON.stringify(oldData)) {
    nextTick(() => updateChartData(newData))
  }
}, { deep: true })

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