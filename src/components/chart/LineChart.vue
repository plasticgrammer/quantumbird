<template>
  <div class="chart-container">
    <div class="chart-wrapper">
      <canvas ref="chartRef" class="chart-canvas"></canvas>
    </div>
    <v-row v-if="totalCount > 3" class="align-center pa-2">
      <v-col cols="auto" class="py-0">
        <v-checkbox v-model="isTop3" color="info" density="compact" hide-details>
          <template #label="{ props: itemProps }">
            <label v-bind="itemProps" class="cursor-pointer text-body-2">上位3件のみ表示</label>
          </template>
        </v-checkbox>
      </v-col>
    </v-row>
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
      return value && Array.isArray(value.labels) && Array.isArray(value.datasets)
    }
  },
  options: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['error'])
const chartRef = ref(null)
const chart = shallowRef(null)
const isTop3 = ref(true)
const totalCount = ref(0)

function updateChart() {
  updateChartInstance({
    chart: chart.value,
    chartData: props.chartData,
    isTop3: isTop3.value,
    onError: (message, error) => {
      console.error(message, error)
      emit('error', error)
    }
  })
  totalCount.value = props.chartData.datasets?.length || 0
}

onMounted(() => {
  const chartOptions = createBaseOptions(props.options)
  chart.value = createChartInstance({
    chartRef: chartRef.value,
    chartData: props.chartData,
    options: chartOptions,
    isTop3: isTop3.value,
    onError: (message, error) => {
      console.error(message, error)
      emit('error', error)
    }
  })
  totalCount.value = props.chartData.datasets?.length || 0
})

onUnmounted(() => {
  if (chart.value) {
    chart.value.destroy()
    chart.value = null
  }
})

watch(isTop3, updateChart)
watch(() => props.chartData, updateChart, { deep: true })
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