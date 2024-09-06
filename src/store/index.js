import { createStore } from 'vuex'
import createPersistedState from 'vuex-persistedstate'
import authModule from './modules/auth'

export default createStore({
  state: {
    loading: false
  },
  mutations: {
    SET_LOADING(state, isLoading) {
      state.loading = isLoading
    }
  },
  actions: {
    setLoading({ commit }, isLoading) {
      commit('SET_LOADING', isLoading)
    }
  },
  getters: {
    isLoading: state => state.loading
  },
  modules: {
    auth: authModule
  },
  plugins: [
    createPersistedState({
      key: 'weekly-report',
      paths: ['auth'], // 指定モジュールのみを永続化
      storage: window.localStorage
    })
  ]
})