import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)
Chart.defaults.datasets.line.tension = 0.3

export const createBaseOptions = (config = {}) => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom'
    },
    title: {
      display: false,
      ...config.title
    }
  },
  scales: {
    y: {
      beginAtZero: config.beginAtZero ?? true,
      ...config.yAxis
    }
  }
})

export const getFilteredData = (datasets, isTop3) => {
  if (!isTop3) return datasets

  return [...datasets]
    .sort((a, b) => {
      const aSum = a.data.reduce((sum, val) => sum + (val || 0), 0)
      const bSum = b.data.reduce((sum, val) => sum + (val || 0), 0)
      return bSum - aSum
    })
    .slice(0, 3)
}

export const createChartInstance = ({
  chartRef,
  chartData,
  options,
  isTop3 = true,
  onError = console.error
}) => {
  if (!chartRef) return null

  try {
    const ctx = chartRef.getContext('2d')
    const datasets = getFilteredData(chartData.datasets || [], isTop3)

    return new Chart(ctx, {
      type: 'line',
      data: {
        labels: chartData.labels,
        datasets
      },
      options
    })
  } catch (error) {
    onError('Error initializing chart:', error)
    return null
  }
}

export const updateChartInstance = ({
  chart,
  chartData,
  isTop3,
  onError = console.error,
  additionalUpdates = () => {}
}) => {
  if (!chart) return

  try {
    const datasets = getFilteredData(chartData.datasets || [], isTop3)
    
    chart.data = {
      labels: chartData.labels,
      datasets
    }

    additionalUpdates(chart)
    chart.update('none')
  } catch (error) {
    onError('Error updating chart:', error)
  }
}