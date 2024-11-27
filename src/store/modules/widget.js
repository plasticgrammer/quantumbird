export default {
  namespaced: true,
  
  state: () => ({
    expandStates: {
      calendar: false,
      overtime: false,
      stress: false,
      organization: false,
      reportRequest: false,
      todo: false,
      weeklyReport: false
    }
  }),

  mutations: {
    SET_WIDGET_STATE(state, { widgetId, isExpanded }) {
      state.expandStates[widgetId] = isExpanded
    }
  },

  actions: {
    toggleWidget({ commit, state }, widgetId) {
      commit('SET_WIDGET_STATE', {
        widgetId,
        isExpanded: !state.expandStates[widgetId]
      })
    }
  }
}