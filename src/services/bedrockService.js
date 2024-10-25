import { apiClient } from './apiClient'

const BASE_PATH = '/bedrock'

// アドバイザーロールの定義
export const advisorRoles = {
  manager: {
    title: 'マネジメントアドバイザー',
    description: '課題解決の視点から業務改善のアドバイスを提供します',
    icon: 'mdi-account-tie',
    color: 'primary',
    image: require('@/assets/images/advisor_manager.gif'),
    role: '【役割：マネジメント支援】課題解決型の包括的な視点を持つマネージャー',
    point: `業務遂行とチーム貢献の観点から、具体的な改善アプローチを提案してください。
数値評価を踏まえた実践的なアドバイスを心がけ、特に以下の点に注目してください：
・タスクの優先順位付けと時間管理
・チームへの貢献度向上
・目標達成のための具体的なアクション`
  },
  mental: {
    title: 'メンタルサポーター',
    description: 'ストレス管理とワークライフバランスのアドバイスを提供します',
    icon: 'mdi-heart',
    color: 'error',
    image: require('@/assets/images/advisor_mental.png'),
    role: '【役割：メンタルケア】共感的傾聴力に長けたメンタルサポーター',
    point: `ストレスマネジメントとワークライフバランスの観点から、具体的なアドバイスを提供してください。
心理的安全性を重視し、特に以下の点に注目してください：
・ストレス軽減のための具体的な施策
・セルフケアの方法
・モチベーション維持のためのアプローチ`
  },
  career: {
    title: 'キャリアアドバイザー',
    description: 'スキル開発とキャリア形成のアドバイスを提供します',
    icon: 'mdi-school',
    color: 'warning',
    image: require('@/assets/images/advisor_career.png'),
    role: '【役割：キャリア支援】スキル分析の専門性を持つキャリアアドバイザー',
    point: `プロフェッショナルとしての成長の観点から、具体的な成長戦略を提案してください。
市場価値の向上を意識し、特に以下の点に注目してください：
・現在の業務から得られる学び
・今後伸ばすべきスキル
・キャリアパスの提案`
  }
}

export const getWeeklyReportAdvice = async (report, advisorRole) => {
  try {
    const result = await apiClient.post(`${BASE_PATH}/advice`, { report, advisorRole })
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
