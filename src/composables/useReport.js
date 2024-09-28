export function useReport() {

  const initialReport = (organizationId, memberUuid, weekString) => {
    const initialRatings = ratingItems.reduce((acc, item) => {
      acc[item.key] = 0
      return acc
    }, {})

    return {
      organizationId,
      memberUuid,
      weekString,
      projects: [{ name: '', workItems: [{ content: '' }] }],
      overtimeHours: 0,
      issues: '',
      improvements: '',
      rating: initialRatings
    }
  }

  const ratingItems = [
    {
      key: 'stress',
      label: 'ストレス度',
      itemLabels: ['余裕あり', '', '', '', '極限状態'],
      negative: true
    },
    {
      key: 'disability',
      label: 'タスク遂行の難易度',
      itemLabels: ['易しい', '', '', '', '難しい'],
      negative: true
    },
    {
      key: 'achievement',
      label: 'タスク目標の達成度',
      itemLabels: ['課題あり', '', '', '', '理想以上'],
      negative: false
    }
  ]

  const statusOptions = [
    { value: 'all', text: '全て', color: 'indigo' },
    { value: 'none', text: '報告なし', color: 'error' },
    { value: 'pending', text: '確認待ち', color: 'success' },
    { value: 'feedback', text: 'フィードバック中', color: 'warning' },
    { value: 'approved', text: '確認済み', color: 'primary' }
  ]

  const getStatusText = (status) => {
    const option = statusOptions.find((e) => e.value === status)
    return option ? option.text : ''
  }

  const getStatusColor = (status) => {
    const option = statusOptions.find((e) => e.value === status)
    return option ? option.color : ''
  }

  return {
    initialReport,
    ratingItems,
    statusOptions,
    getStatusText,
    getStatusColor
  }
}  