// src/composables/useReport.js
import { ref } from 'vue'

export function useReport() {
  const initialReport = () => ({
    projects: [{ name: '', workItems: [{ content: '' }] }],
    overtimeHours: 0,
    issues: ''
  })

  const report = ref(initialReport())

  const formatDateRange = (start, end) => {
    const options = { year: 'numeric', month: 'long', day: 'numeric' }
    return `${start.toLocaleDateString('ja-JP', options)} - ${end.toLocaleDateString('ja-JP', options)}`
  }

  const submitReport = (submittedReport) => {
    // ここでレポートの送信処理を実装
    console.log('Report submitted:', submittedReport)
    // API呼び出しなどの処理を追加
  }

  return {
    initialReport,
    report,
    formatDateRange,
    submitReport
  }
}