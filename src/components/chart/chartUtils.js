import { ref } from 'vue'
import { Chart, registerables } from 'chart.js'

// Register all Chart.js components
Chart.register(...registerables)

export function useChart(chartType, createChartOptions) {
  const chartRef = ref(null)
  let chartInstance = null
  const selectedDatasetIndex = ref(null)

  const updateDatasetVisibility = () => {
    if (!chartInstance) return

    const datasets = chartInstance.data.datasets
    datasets.forEach((dataset, index) => {
      const meta = chartInstance.getDatasetMeta(index)
      if (selectedDatasetIndex.value === null) {
        meta.hidden = false
      } else {
        meta.hidden = index !== selectedDatasetIndex.value
      }
    })
    chartInstance.update()
  }

  const getChartOptions = () => ({
    ...createChartOptions(),
    plugins: {
      ...createChartOptions().plugins,
      legend: {
        ...createChartOptions().plugins?.legend,
        onClick: (event, legendItem) => {
          const index = legendItem.datasetIndex
          
          if (selectedDatasetIndex.value === index) {
            selectedDatasetIndex.value = null
          } else {
            selectedDatasetIndex.value = index
          }

          updateDatasetVisibility()
        }
      }
    }
  })

  const createChart = (data) => {
    const ctx = chartRef.value.getContext('2d')
    return new Chart(ctx, {
      type: chartType,
      data: data,
      options: getChartOptions()
    })
  }

  const initChart = (data) => {
    if (chartRef.value && data) {
      try {
        chartInstance = createChart(data)
        selectedDatasetIndex.value = null
        updateDatasetVisibility()
      } catch (error) {
        console.error('Failed to create chart:', error)
      }
    }
  }

  const updateChart = (data) => {
    if (chartInstance) {
      chartInstance.data = data
      chartInstance.options = getChartOptions()
      if (selectedDatasetIndex.value !== null && selectedDatasetIndex.value >= data.datasets.length) {
        selectedDatasetIndex.value = null
      }
      updateDatasetVisibility()
    } else {
      initChart(data)
    }
  }

  return {
    chartRef,
    initChart,
    updateChart
  }
}