<template>
  <div class="chart-container">
    <div class="chart-wrapper">
      <canvas ref="chartRef" class="chart-canvas"></canvas>
    </div>
  </div>
</template>

<script setup>
import { ref, shallowRef, watch, onMounted, onUnmounted } from 'vue'
import { createBaseOptions, createChartInstance, updateChartInstance } from './chartUtils'

const props = defineProps({
  chartData: {
    type: Object,
    required: true,
    validator: (value) => {
      if (!value || !Array.isArray(value.labels) || !Array.isArray(value.datasets)) {
        return false
      }
      // データセットの構造を検証
      return value.datasets.every(dataset => 
        dataset && Array.isArray(dataset.data) && 
        dataset.data.length === value.labels.length
      )
    }
  },
  options: {
    type: Object,
    default: () => ({})
  },
  isTop3: {
    type: Boolean,
    default: true
  },
  averageOptions: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['error'])
const chartRef = ref(null)
const chart = shallowRef(null)
const totalCount = ref(0)

function handleError(message, error) {
  console.error(message, error)
  emit('error', { message, error })
}

function updateChart() {
  if (!chart.value || !props.chartData) return
  
  updateChartInstance({
    chart: chart.value,
    chartData: props.chartData,
    isTop3: props.isTop3,
    options: props.options,
    averageOptions: props.averageOptions,
    onError: handleError
  })
  totalCount.value = props.chartData.datasets?.length || 0
}

onMounted(() => {
  const chartOptions = createBaseOptions(props.options)
  chart.value = createChartInstance({
    chartRef: chartRef.value,
    chartData: props.chartData,
    options: chartOptions,
    isTop3: props.isTop3,
    averageOptions: props.averageOptions,
    onError: handleError
  })
  totalCount.value = props.chartData.datasets?.length || 0
})

onUnmounted(() => {
  if (chart.value) {
    chart.value.destroy()
    chart.value = null
  }
})

watch(
  [
    () => props.options, 
    () => props.chartData, 
    () => props.isTop3,
    () => props.averageOptions
  ],
  updateChart,
  { deep: true }
)
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