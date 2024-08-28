import { createStore } from 'vuex'
import createPersistedState from 'vuex-persistedstate'
import authModule from './modules/auth'

export default createStore({
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