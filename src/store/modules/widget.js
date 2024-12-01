export const WIDGET_DEFINITIONS = {
  calendar: {
    component: 'CalendarWidget',
    title: '報告状況',
    defaultExpanded: true,
    defaultVisible: true
  },
  overtime: {
    component: 'OvertimeChart',
    title: '残業時間の遷移',
    defaultExpanded: false,
    defaultVisible: true
  },
  stress: {
    component: 'StressChart',
    title: 'ストレス評価の遷移',
    defaultExpanded: false,
    defaultVisible: true
  },
  disability: {
    component: 'DisabilityChart',
    title: 'タスク難易度の遷移',
    defaultExpanded: false,
    defaultVisible: false
  },
  achievement: {
    component: 'AchievementChart',
    title: 'タスク達成度の遷移',
    defaultExpanded: false,
    defaultVisible: false
  },
  organization: {
    component: 'OrganizationWidget',
    title: '組織情報',
    defaultExpanded: false,
    defaultVisible: true
  },
  reportRequest: {
    component: 'ReportRequestWidget',
    title: '報告依頼',
    defaultExpanded: false,
    defaultVisible: true
  },
  todo: {
    component: 'TodoListWidget',
    title: 'やることリスト',
    defaultExpanded: false,
    defaultVisible: true
  },
  weeklyReport: {
    component: 'WeeklyReportWidget',
    title: 'メンバーの週次報告',
    defaultExpanded: false,
    defaultVisible: true
  }
}

const createInitialState = () => ({
  expandStates: Object.fromEntries(
    Object.entries(WIDGET_DEFINITIONS)
      .map(([id, def]) => [id, def.defaultExpanded ?? false])
  ),
  widgetOrder: Object.keys(WIDGET_DEFINITIONS),
  widgetVisibility: Object.fromEntries(
    Object.entries(WIDGET_DEFINITIONS)
      .map(([id, def]) => [id, def.defaultVisible ?? false])
  )
})

export default {
  namespaced: true,
  state: createInitialState,

  mutations: {
    SET_WIDGET_STATE(state, { widgetId, isExpanded }) {
      state.expandStates[widgetId] = isExpanded
    },
    SET_WIDGET_ORDER(state, order) {
      // 表示中のウィジェットと非表示のウィジェットを分離して管理
      const currentVisible = state.widgetOrder
        .filter(id => state.widgetVisibility[id])
      const hidden = state.widgetOrder
        .filter(id => !state.widgetVisibility[id])

      // 順序の整合性チェック
      if (order.length === currentVisible.length &&
        order.every(id => state.widgetVisibility[id])) {
        state.widgetOrder = [...order, ...hidden]
      }
    },
    SET_WIDGET_VISIBILITY(state, { widgetId, isVisible }) {
      // 可視性の更新
      state.widgetVisibility = {
        ...state.widgetVisibility,
        [widgetId]: isVisible
      }

      // widgetOrderの更新
      if (isVisible && !state.widgetOrder.includes(widgetId)) {
        // 表示に切り替えた場合、widgetOrderに追加
        state.widgetOrder.push(widgetId)
      }
    }
  },

  actions: {
    toggleWidget({ commit, state }, widgetId) {
      commit('SET_WIDGET_STATE', {
        widgetId,
        isExpanded: !state.expandStates[widgetId]
      })
    },
    updateWidgetOrder({ commit, state }, order) {
      // 順序の更新前に検証
      if (Array.isArray(order) && order.length > 0 &&
        order.every(id => state.widgetOrder.includes(id))) {
        commit('SET_WIDGET_ORDER', order)
      }
    },
    async toggleWidgetVisibility({ commit, state }, widgetId) {
      const newVisibility = !state.widgetVisibility[widgetId]

      // 最後の表示中のウィジェットを非表示にすることを防ぐ
      const visibleCount = Object.values(state.widgetVisibility).filter(Boolean).length
      if (!newVisibility && visibleCount <= 1) {
        return false
      }

      commit('SET_WIDGET_VISIBILITY', {
        widgetId,
        isVisible: newVisibility
      })
      return true
    }
  }
}