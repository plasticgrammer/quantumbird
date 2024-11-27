export default {
  namespaced: true,
  
  state: () => ({
    expandStates: {
      calendar: true,
      overtime: false,
      stress: false,
      organization: false,
      reportRequest: false,
      todo: false,
      weeklyReport: false
    },
    widgetOrder: [
      'calendar',
      'overtime',
      'stress',
      'organization',
      'reportRequest',
      'todo',
      'weeklyReport'
    ],
    widgetVisibility: {
      calendar: true,
      overtime: true,
      stress: true,
      organization: true,
      reportRequest: true,
      todo: true,
      weeklyReport: true
    }
  }),

  mutations: {
    SET_WIDGET_STATE(state, { widgetId, isExpanded }) {
      state.expandStates[widgetId] = isExpanded
    },
    SET_WIDGET_ORDER(state, order) {
      state.widgetOrder = [...order]
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
    updateWidgetOrder({ commit }, order) {
      commit('SET_WIDGET_ORDER', order)
    },
    toggleWidgetVisibility({ commit, state }, widgetId) {
      commit('SET_WIDGET_VISIBILITY', {
        widgetId,
        isVisible: !state.widgetVisibility[widgetId]
      })
    }
  }
}