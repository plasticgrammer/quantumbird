import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)
Chart.defaults.datasets.line.tension = 0.3
Chart.defaults.datasets.line.spanGaps = true // 欠損値をスキップして線を繋ぐ

export const createBaseOptions = (config = {}) => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom',
      onClick: (event, legendItem, legend) => {
        const chart = legend.chart
        const index = legendItem.datasetIndex
        
        // 現在の表示状態を確認
        const isOnlyThisVisible = chart.data.datasets.every((dataset, i) => 
          i === index ? chart.isDatasetVisible(i) : !chart.isDatasetVisible(i)
        )
        
        if (isOnlyThisVisible) {
          // 既に対象系列のみが表示されている場合は全て表示
          chart.data.datasets.forEach((dataset, i) => {
            chart.setDatasetVisibility(i, true)
          })
        } else {
          // それ以外の場合は対象系列のみ表示
          chart.data.datasets.forEach((dataset, i) => {
            chart.setDatasetVisibility(i, i === index)
          })
        }
        
        chart.update()
      },
      /*
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
      */
    },
    title: {
      display: false,
      ...config.title
    }
  },
  scales: config.scales || {
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

  const {
    useExponential = false,
    alpha = 0.35 // 最新データに指定値の重み、必要に応じて0.1-0.5の範囲で調整可能
  } = options

  const sortedDatasets = [...datasets]
    .sort((a, b) => {
      const aAvg = useExponential ?
        getExponentialAverage(a.data, alpha) :
        getValidAverage(a.data)
      const bAvg = useExponential ?
        getExponentialAverage(b.data, alpha) :
        getValidAverage(b.data)
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