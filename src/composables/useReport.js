export function useReport() {
  const statusOptions = [
    { value: 'all', text: '全て', color: 'indigo' },
    { value: 'none', text: '報告なし', color: 'error' },
    { value: 'pending', text: '確認待ち', color: 'primary' },
    { value: 'feedback', text: 'フィードバック中', color: 'warning' },
    { value: 'approved', text: '確認済み', color: 'success' }
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
    statusOptions,
    getStatusText,
    getStatusColor
  }
}  