import { createStore } from 'vuex'
import userModule from './modules/user'

export default createStore({
  modules: {
    user: userModule
  }
})