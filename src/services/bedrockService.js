import { apiClient } from './apiClient'

const BASE_PATH = '/bedrock'

export const getWeeklyReportAdvice = async (report) => {
  try {
    const result = await apiClient.post(`${BASE_PATH}/advice`, { report })
    return {
      advice: result.advice || '',
      weekString: result.weekString,
      memberUuid: result.memberUuid
    }
  } catch (error) {
    console.error('Error getting weekly report advice:', error)
    throw new Error('週次報告のアドバイス取得に失敗しました。')
  }
}
