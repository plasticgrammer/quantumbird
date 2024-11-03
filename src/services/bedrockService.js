import { apiClient } from './apiClient'

const BASE_PATH = '/bedrock'

// アドバイザーロールの定義
export const advisorRoles = {
  manager: {
    title: 'マネジメントアドバイザー',
    description: '課題解決の視点から業務改善のアドバイスを提供します',
    icon: 'mdi-account-supervisor',
    color: 'pink',
    image: require('@/assets/images/advisor_manager.gif')
  },
  career: {
    title: 'キャリアアドバイザー',
    description: 'スキル開発とキャリア形成のアドバイスを提供します',
    icon: 'mdi-school',
    color: 'deep-purple',
    image: require('@/assets/images/advisor_career.png')
  },
  mental: {
    title: 'メンタルサポーター',
    description: 'ストレス管理とセルフケアのアドバイスを提供します',
    icon: 'mdi-heart',
    color: 'red',
    image: require('@/assets/images/advisor_mental.png')
  },
  reframe: {
    title: 'リフレーミングマスター',
    description: '課題をポジティブ視点で捉え直すアドバイスを提供します',
    icon: 'mdi-border-outside',
    color: 'cyan',
    image: require('@/assets/images/advisor_reframe.png')
  },
  scenario: {
    title: 'ストーリーアーキテクト',
    description: '成長のストーリーとして状況を再構築します',
    icon: 'mdi-script-text',
    color: 'orange-darken-2',
    image: require('@/assets/images/advisor_scenario.png')
  },
  detective: {
    title: 'ミステリーディテクティブ',
    description: '状況の背後にある真相を探り出します',
    icon: 'mdi-magnify',
    color: 'brown',
    image: require('@/assets/images/advisor_detective.png')
  },
  timeNavi: {
    title: 'クロノスナビゲーター',
    description: '時間軸を超えた視点でアドバイスを提供します',
    icon: 'mdi-clock-time-eight',
    color: 'indigo',
    image: require('@/assets/images/advisor_time.png')
  },
}

export const getWeeklyReportAdvice = async (report, advisorRole) => {
  try {
    const result = await apiClient.post(`${BASE_PATH}/advice`, { report, advisorRole })
    return {
      advice: result.advice || '',
      weekString: result.weekString,
      memberUuid: result.memberUuid,
      remainingTickets: result.remainingTickets || 0
    }
  } catch (error) {
    console.error('Error getting weekly report advice:', error)
    throw new Error('週次報告のアドバイス取得に失敗しました。')
  }
}
