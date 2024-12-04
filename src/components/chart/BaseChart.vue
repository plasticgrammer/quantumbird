<template>
  <BaseWidget :widget-id="widgetId" :title="title" icon="mdi-chart-line">
    <template #header-append>
      <v-checkbox
        v-if="chartData.datasets?.length > 3"
        v-model="isRecentTop3"
        v-tooltip:top="'直近のデータを重視して上位3件を表示'"
        color="blue-grey-lighten-3"
        density="compact"
        hide-details
      >
        <template #label>
          <span class="text-body-2">直近上位3件</span>
        </template>
      </v-checkbox>
    </template>
    <LineChart 
      :chart-data="chartData" 
      :options="chartOptions" 
      :is-top3="isRecentTop3"
      :average-options="averageOptions"
    />
  </BaseWidget>
</template>

<script setup>
import { computed, ref } from 'vue'
import BaseWidget from '../widget/BaseWidget.vue'
import LineChart from './LineChart.vue'

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
  min: {
    type: Number,
    default: 0.8
  },
  max: {
    type: Number,
    default: 5.2
  },
  yAxisConfig: {
    type: Object,
    required: true
  }
})

const isRecentTop3 = ref(true)

const chartOptions = computed(() => ({
  yAxis: {
    min: props.min,
    max: props.max,
    ...props.yAxisConfig
  }
}))

const averageOptions = computed(() => ({
  useExponential: isRecentTop3.value,
  alpha: 0.3
}))
</script>

<style scoped>
:deep(.v-checkbox) {
  margin-top: 0;
  margin-bottom: 0;
}
</style>