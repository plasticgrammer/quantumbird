import { createStore } from 'vuex'

export default createStore({
  state: {
    reports: []
  },
  mutations: {
    SET_REPORTS(state, reports) {
      state.reports = reports
    }
  },
  actions: {
    fetchReports({ commit }) {
      // Here you would typically make an API call
      // For now, we'll just set some dummy data
      const dummyReports = [
        { id: 1, title: 'Week 1 Report', content: 'Content for week 1' },
        { id: 2, title: 'Week 2 Report', content: 'Content for week 2' }
      ]
      commit('SET_REPORTS', dummyReports)
    }
  },
  getters: {
    allReports: (state) => state.reports
  }
})