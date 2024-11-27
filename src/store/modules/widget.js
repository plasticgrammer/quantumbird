export default {
  namespaced: true,
  
  state: () => {
    const defaultOrder = [
      'calendar',
      'overtime',
      'stress',
      'organization',
      'reportRequest',
      'todo',
      'weeklyReport'
    ]

    const defaultVisibility = {
      calendar: true,
      overtime: true,
      stress: true,
      organization: true,
      reportRequest: true,
      todo: true,
      weeklyReport: true
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
      widgetOrder: defaultOrder,
      widgetVisibility: defaultVisibility
    }
  },

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