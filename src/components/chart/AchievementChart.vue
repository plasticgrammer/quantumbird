<template>
  <line-chart :chart-data="chartData" :options="chartOptions" />
</template>

<script setup>
import { defineProps } from 'vue'
import LineChart from './LineChart.vue'

const chartOptions = {
  beginAtZero: false,
  yAxis: {
    min: 0.8,
    max: 5.2,
    ticks: {
      stepSize: 1,
      precision: 0,
      callback: (value) => {
        if (value === 1) return '課題あり'
        if (value === 5) return '理想以上'
        return ''
      },
      includeBounds: false
    },
    title: {
      display: true,
      text: 'タスク達成度'
    },
    grid: {
      color: (context) => context.tick.value === 5 ? 'rgba(0, 0, 0, 0.2)' : 'rgba(0, 0, 0, 0.1)'
    }
  }
}

defineProps({
  chartData: {
    type: Object,
    required: true
  }
})
</script>