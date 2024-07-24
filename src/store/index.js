import { createStore } from 'vuex'
import createPersistedState from 'vuex-persistedstate'
import userModule from './modules/user'

export default createStore({
  modules: {
    user: userModule
  },
  plugins: [
    createPersistedState({
      key: 'weekly-report',
      paths: ['user'], // userモジュールのみを永続化
      storage: window.localStorage
    })
  ]
})