
import { getCurrentUser, signOut } from 'aws-amplify/auth'

export default {
  namespaced: true,
  state: () => ({
    user: null
  }),
  mutations: {
    setUser(state, user) {
      state.user = user
    }
  },
  actions: {
    async fetchUser({ commit }) {
      try {
        const user = await getCurrentUser()
        const userInfo = {
          organizationId: user.attributes['custom:organizationId'],
          username: user.username,
          email: user.attributes.email,
        }
        commit('setUser', userInfo)
      } catch (error) {
        console.error('Error fetching user:', error)
        commit('setUser', null)
      }
    },
    async signOut({ commit }) {
      try {
        await signOut()
        commit('setUser', null)
      } catch (error) {
        console.error('Error signing out:', error)
      }
    }
  },
  getters: {
    organizationId: (state) => {
      return state.user.organizationId
    },
    isAuthenticated: state => !!state.user
  }
}