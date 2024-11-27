export default {
  namespaced: true,

  state: () => ({
    expandStates: {
      calendar: true,
      overtime: false,
      stress: false,
      disability: false,
      achievement: false,
      organization: false,
      reportRequest: false,
      todo: false,
      weeklyReport: false,
    },
    widgetOrder: [
      'calendar',
      'overtime',
      'stress',
      'disability',
      'achievement',
      'organization',
      'reportRequest',
      'todo',
      'weeklyReport',
    ],
    widgetVisibility: {
      calendar: true,
      overtime: true,
      stress: true,
      disability: false,
      achievement: false,
      organization: true,
      reportRequest: true,
      todo: true,
      weeklyReport: true,
    }
  }),

  mutations: {
    SET_WIDGET_STATE(state, { widgetId, isExpanded }) {
      state.expandStates[widgetId] = isExpanded
    },
    SET_WIDGET_ORDER(state, order) {
      // 新しい順序を設定する前に、既存のウィジェットIDが全て含まれていることを確認
      const existingIds = new Set(state.widgetOrder)
      const newOrder = order.filter(id => existingIds.has(id))

      // 表示されていないウィジェットの順序を維持
      const remainingIds = state.widgetOrder.filter(id => !order.includes(id))
      state.widgetOrder = [...newOrder, ...remainingIds]
    },
    SET_WIDGET_VISIBILITY(state, { widgetId, isVisible }) {
      state.widgetVisibility = {
        ...state.widgetVisibility,
        [widgetId]: isVisible
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