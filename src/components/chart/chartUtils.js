import { ref } from 'vue'
import { Chart, registerables } from 'chart.js'

// Register all Chart.js components
Chart.register(...registerables)

// グローバルデフォルト設定
Chart.defaults.datasets.line.tension = 0.3
Chart.defaults.datasets.line.pointRadius = 0

export function useChart(chartType, createChartOptions) {
  const chartRef = ref(null)
  const selectedDatasetIndex = ref(null)

  const updateDatasetVisibility = (instance) => {
    if (!instance) {
      console.error('Instance is undefined in updateDatasetVisibility')
      return
    }

    // Check if the instance is a Chart object
    if (instance instanceof Chart) {
      if (!instance.data || !Array.isArray(instance.data.datasets)) {
        console.error('Invalid chart data structure', instance.data)
        return
      }

      const datasets = instance.data.datasets
      datasets.forEach((dataset, index) => {
        const meta = instance.getDatasetMeta(index)
        if (meta) {
          meta.hidden = selectedDatasetIndex.value !== null && index !== selectedDatasetIndex.value
        } else {
          console.warn(`Dataset meta not found for index ${index}`)
        }
      })
      instance.update('none') // アニメーションなしで更新
    } else {
      // Handle Legend click
      if (instance.chart && instance.chart instanceof Chart) {
        updateDatasetVisibility(instance.chart)
      } else {
        console.error('Invalid Legend instance or missing chart reference', instance)
      }
    }
  }

  const getChartOptions = () => ({
    ...createChartOptions(),
    plugins: {
      ...createChartOptions().plugins,
      legend: {
        ...createChartOptions().plugins?.legend,
        onClick: (event, legendItem, legend) => {
          const index = legendItem.datasetIndex

          selectedDatasetIndex.value = selectedDatasetIndex.value === index ? null : index

          updateDatasetVisibility(legend)
        }
      }
    }
  })

  const createChart = (data) => {
    if (!chartRef.value) {
      throw new Error('Chart reference is not available')
    }

    const ctx = chartRef.value.getContext('2d')
    if (!ctx) {
      throw new Error('Unable to get 2D context from canvas')
    }

    if (!data || !Array.isArray(data.datasets) || !Array.isArray(data.labels)) {
      throw new Error('Invalid chart data format')
    }

    return new Chart(ctx, {
      type: chartType,
      data: data,
      options: getChartOptions()
    })
  }

  const updateChart = (chartInstance, data) => {
    if (!chartInstance || !(chartInstance instanceof Chart)) {
      throw new Error('Invalid Chart instance')
    }

    if (!data || !Array.isArray(data.datasets) || !Array.isArray(data.labels)) {
      throw new Error('Invalid chart data format')
    }

    chartInstance.data = data
    chartInstance.options = getChartOptions()

    if (selectedDatasetIndex.value !== null && selectedDatasetIndex.value >= data.datasets.length) {
      selectedDatasetIndex.value = null
    }

    updateDatasetVisibility(chartInstance)
  }

  return {
    chartRef,
    createChart,
    updateChart
  }
}