
import { fetchUserAttributes, signOut } from 'aws-amplify/auth'

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
        const attributes = await fetchUserAttributes()
        const userInfo = {
          organizationId: attributes['custom:organizationId'],
          username: attributes.name,
          email: attributes.email,
        }
        console.info('fetchUser:', userInfo)
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
    organizationId: (state) => state.user?.organizationId,
    name: (state) => state.user?.username,
    email: (state) => state.user?.email,
    isAuthenticated: state => !!state.user
  }
}