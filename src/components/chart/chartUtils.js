import { ref } from 'vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

Chart.defaults.datasets.line.tension = 0.3

export function useChart(chartType, createChartOptions) {
  const chartRef = ref(null)
  const hoveredDatasetIndex = ref(null)

  const updateDatasetVisibility = (chart, index) => {
    chart.data.datasets.forEach((dataset, i) => {
      chart.setDatasetVisibility(i, i === index || index === null)
    })
    chart.update('none')
  }

  const getChartOptions = () => ({
    ...createChartOptions(),
    plugins: {
      ...createChartOptions().plugins,
      legend: {
        ...createChartOptions().plugins?.legend,
        onHover: (event, legendItem, legend) => {
          const index = legendItem.datasetIndex
          if (hoveredDatasetIndex.value !== index) {
            hoveredDatasetIndex.value = index
            updateDatasetVisibility(legend.chart, index)
          }
        },
        onLeave: (event, legendItem, legend) => {
          hoveredDatasetIndex.value = null
          updateDatasetVisibility(legend.chart, null)
        }
      }
    },
    onHover: (event, activeElements, chart) => {
      if (activeElements.length === 0) {
        hoveredDatasetIndex.value = null
        updateDatasetVisibility(chart, null)
      }
    }
  })

  const createChart = (data) => {
    try {
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

      const chartInstance = new Chart(ctx, {
        type: chartType,
        data: data,
        options: getChartOptions()
      })
      return chartInstance

    } catch (error) {
      console.error('Error creating chart:', error)
      return null
    }
  }

  const updateChart = (chartInstance, data) => {
    try {
      if (!chartInstance || !(chartInstance instanceof Chart)) {
        throw new Error('Invalid Chart instance')
      }

      if (!data || !Array.isArray(data.datasets) || !Array.isArray(data.labels)) {
        throw new Error('Invalid chart data format')
      }

      chartInstance.data = data
      chartInstance.options = getChartOptions()
      chartInstance.update()

    } catch (error) {
      console.error('Error updating chart:', error)
    }
  }

  return {
    chartRef,
    createChart,
    updateChart
  }
}