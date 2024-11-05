<template>
  <div class="chart-container">
    <div class="chart-wrapper">
      <canvas ref="chartRef" class="chart-canvas"></canvas>
    </div>
    <v-row v-if="totalCount > 3" class="align-center pa-2">
      <v-col cols="auto" class="py-0">
        <v-checkbox
          v-model="isTop3"
          color="info"
          density="compact"
          hide-details
        >
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
import { 
  createBaseOptions, 
  createChartInstance, 
  updateChartInstance, 
  getFilteredData 
} from './chartUtils'

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
const chart = shallowRef(null)
const isTop3 = ref(true)
const totalCount = ref(0)

function getMaxValue(datasets) {
  if (!datasets.length) return 3.0
  const allValues = datasets.flatMap(d => d.data)
  return Math.max(...allValues.filter(v => typeof v === 'number'), 3.0)
}

function getChartOptions() {
  const datasets = getFilteredData(props.chartData.datasets || [], isTop3.value)
  const maxValue = getMaxValue(datasets)

  return createBaseOptions({
    yAxis: {
      max: maxValue,
      ticks: {
        stepSize: Math.ceil(maxValue / 5)
      },
      title: {
        display: true,
        text: props.yAxisTitle
      }
    }
  })
}

function updateChart() {
  updateChartInstance({
    chart: chart.value,
    chartData: props.chartData,
    isTop3: isTop3.value,
    additionalUpdates: (chartInstance) => {
      const datasets = getFilteredData(props.chartData.datasets || [], isTop3.value)
      const maxValue = getMaxValue(datasets)
      
      chartInstance.options.scales.y.max = maxValue
      chartInstance.options.scales.y.ticks.stepSize = Math.ceil(maxValue / 5)
      chartInstance.options.scales.y.title.text = props.yAxisTitle
    }
  })
  totalCount.value = props.chartData.datasets?.length || 0
}

onMounted(() => {
  chart.value = createChartInstance({
    chartRef: chartRef.value,
    chartData: props.chartData,
    options: getChartOptions(),
    isTop3: isTop3.value
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
watch(() => [props.chartData, props.yAxisTitle], updateChart, { deep: true })
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
