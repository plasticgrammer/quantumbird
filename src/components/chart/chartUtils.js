import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)
Chart.defaults.datasets.line.tension = 0.3

export const createBaseOptions = (config = {}) => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom',
      onHover: (event, legendItem, legend) => {
        const chart = legend.chart
        chart.data.datasets.forEach((dataset, index) => {
          chart.setDatasetVisibility(index, false)
        })
        chart.setDatasetVisibility(legendItem.datasetIndex, true)
        chart.update()
      },
      onLeave: (event, legendItem, legend) => {
        const chart = legend.chart
        chart.data.datasets.forEach((dataset, index) => {
          chart.setDatasetVisibility(index, true)
        })
        chart.update()
      }
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
  if (!datasets?.length || !isTop3) return datasets || []

  return [...datasets]
    .sort((a, b) => {
      const aSum = a.data.reduce((sum, val) => sum + (Number(val) || 0), 0)
      const bSum = b.data.reduce((sum, val) => sum + (Number(val) || 0), 0)
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
  options,
  onError = console.error
}) => {
  if (!chart || !chartData) return

  try {
    const datasets = getFilteredData(chartData.datasets, isTop3)
    
    chart.data = { labels: chartData.labels, datasets }
    if (options) {
      chart.options = createBaseOptions(options)
    }
    
    chart.update()
  } catch (error) {
    onError('チャートの更新に失敗しました', error)
  }
}