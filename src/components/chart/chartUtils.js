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

const getExponentialAverage = (data, alpha = 0.3) => {
  const validValues = data.filter(val => val !== null && val !== undefined && !isNaN(Number(val)))
  if (validValues.length === 0) return 0
  
  let ema = Number(validValues[0])
  for (let i = 1; i < validValues.length; i++) {
    ema = alpha * Number(validValues[i]) + (1 - alpha) * ema
  }
  return ema
}

const getValidAverage = (data) => {
  const validValues = data.filter(val => val !== null && val !== undefined && !isNaN(Number(val)))
  if (validValues.length === 0) return 0
  return validValues.reduce((sum, val) => sum + Number(val), 0) / validValues.length
}

export const getFilteredData = (datasets, isTop3, options = {}) => {
  if (!datasets?.length || !isTop3) return datasets || []

  const { useExponential = false, alpha = 0.3 } = options

  // デバッグ用のログ出力
  console.log('Filtering with:', { useExponential, alpha })

  const sortedDatasets = [...datasets]
    .sort((a, b) => {
      const aAvg = useExponential ? 
        getExponentialAverage(a.data, alpha) : 
        getValidAverage(a.data)
      const bAvg = useExponential ? 
        getExponentialAverage(b.data, alpha) : 
        getValidAverage(b.data)

      // デバッグ用のログ出力
      console.log(`Average for ${a.label}: ${aAvg}`)
      console.log(`Average for ${b.label}: ${bAvg}`)

      return bAvg - aAvg
    })
    .slice(0, 3)

  return sortedDatasets
}

export const createChartInstance = ({
  chartRef,
  chartData,
  options,
  isTop3 = true,
  averageOptions = {},
  onError = console.error
}) => {
  if (!chartRef) return null

  try {
    const ctx = chartRef.getContext('2d')
    const datasets = getFilteredData(chartData.datasets || [], isTop3, averageOptions)

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
  averageOptions = {},
  onError = console.error
}) => {
  if (!chart || !chartData) return

  try {
    const datasets = getFilteredData(chartData.datasets, isTop3, averageOptions)

    chart.data = { labels: chartData.labels, datasets }
    if (options) {
      chart.options = createBaseOptions(options)
    }

    chart.update()
  } catch (error) {
    onError('チャートの更新に失敗しました', error)
  }
}