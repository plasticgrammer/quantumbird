<template>
  <BaseChart
    :widget-id="widgetId"
    :title="title"
    :chart-data="chartData"
    :min="0"
    :max="currentMaxValue"
    :y-axis-config="yAxisConfig"
  />
</template>

<script setup>
import { computed } from 'vue'
import BaseChart from './BaseChart.vue'

const props = defineProps({
  widgetId: {
    type: String,
    required: true
  },
  title: {
    type: String,
    required: true
  },
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

function getMaxValue(datasets) {
  if (!datasets?.length) return 3.0
  const allValues = datasets.flatMap(d => d.data || [])
    .filter(v => v !== null && v !== undefined)
    .map(v => Number(v))
    .filter(v => !isNaN(v))
  if (allValues.length === 0) return 3.0
  return Math.max(3.0, Math.ceil(Math.max(...allValues)))
}

const currentMaxValue = computed(() => getMaxValue(props.chartData.datasets))
const currentStepSize = computed(() => Math.max(1, Math.ceil(currentMaxValue.value / 5)))

const yAxisConfig = computed(() => ({
  ticks: { 
    stepSize: currentStepSize.value,
    precision: 0,
    callback: function(value) {
      return value + 'h'
    } 
  },
  title: { display: true, text: props.yAxisTitle },
  afterDataLimits: (scale) => {
    scale.max = getMaxValue(props.chartData.datasets)
  }
}))
</script>
