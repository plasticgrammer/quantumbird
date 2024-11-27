export default {
  namespaced: true,
  
  state: () => {
    // 初期化時に必ずデフォルト値を持つように
    const defaultOrder = [
      'calendar',
      'overtime',
      'stress',
      'organization',
      'reportRequest',
      'todo',
      'weeklyReport'
    ]

    let savedOrder
    try {
      savedOrder = JSON.parse(localStorage.getItem('widgetOrder'))
      // 保存された順序が有効か検証
      if (!Array.isArray(savedOrder) || 
          !savedOrder.every(id => defaultOrder.includes(id)) ||
          savedOrder.length !== defaultOrder.length) {
        savedOrder = null
      }
    } catch {
      savedOrder = null
    }

    return {
      expandStates: {
        calendar: true,
        overtime: false,
        stress: false,
        organization: false,
        reportRequest: false,
        todo: false,
        weeklyReport: false
      },
      widgetOrder: savedOrder || defaultOrder
    }
  },

  mutations: {
    SET_WIDGET_STATE(state, { widgetId, isExpanded }) {
      state.expandStates[widgetId] = isExpanded
    },
    SET_WIDGET_ORDER(state, order) {
      state.widgetOrder = [...order]
      localStorage.setItem('widgetOrder', JSON.stringify(order))
    }
  },

  actions: {
    toggleWidget({ commit, state }, widgetId) {
      commit('SET_WIDGET_STATE', {
        widgetId,
        isExpanded: !state.expandStates[widgetId]
      })
    },
    updateWidgetOrder({ commit }, order) {
      commit('SET_WIDGET_ORDER', order)
    }
  }
}