import { createStore } from 'vuex'
import createPersistedState from 'vuex-persistedstate'
import authModule from './modules/auth'
import widget from './modules/widget'

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
    auth: authModule,
    widget
  },
  plugins: [
    createPersistedState({
      key: 'weekly-report',
      paths: ['auth', 'widget'], // 永続化モジュールを指定（直接localStorageを操作しなくてよい）
      storage: window.localStorage
    })
  ]
})