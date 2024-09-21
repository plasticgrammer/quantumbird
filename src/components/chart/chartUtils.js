import { ref } from 'vue'
import { Chart, registerables } from 'chart.js'

// Register all Chart.js components
Chart.register(...registerables)

export function useChart(chartType, createChartOptions) {
  const chartRef = ref(null)
  const selectedDatasetIndex = ref(null)

  const updateDatasetVisibility = (chartInstance) => {
    if (!chartInstance) return

    const datasets = chartInstance.data.datasets
    datasets.forEach((dataset, index) => {
      const meta = chartInstance.getDatasetMeta(index)
      meta.hidden = selectedDatasetIndex.value !== null && index !== selectedDatasetIndex.value
    })
    chartInstance.update()
  }

  const getChartOptions = () => ({
    ...createChartOptions(),
    plugins: {
      ...createChartOptions().plugins,
      legend: {
        ...createChartOptions().plugins?.legend,
        onClick: (event, legendItem, chart) => {
          const index = legendItem.datasetIndex
          
          selectedDatasetIndex.value = selectedDatasetIndex.value === index ? null : index

          updateDatasetVisibility(chart)
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
    if (!chartInstance) {
      throw new Error('Chart instance is not available')
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
    chartInstance.update()
  }

  return {
    chartRef,
    createChart,
    updateChart
  }
}