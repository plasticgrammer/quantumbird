import { fetchUserAttributes, signOut, fetchAuthSession } from 'aws-amplify/auth'

export default {
  namespaced: true,
  state: () => ({
    user: null,
    token: null
  }),
  mutations: {
    setUser(state, user) {
      state.user = user
    },
    setToken(state, token) {
      state.token = token
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
        commit('setToken', null)
      } catch (error) {
        console.error('Error signing out:', error)
      }
    },
    async fetchAuthToken({ commit }) {
      try {
        const { tokens } = await fetchAuthSession()
        if (tokens && tokens.idToken) {
          commit('setToken', tokens.idToken.toString())
          return tokens.idToken.toString()
        }
        return null
      } catch (error) {
        console.error('Error fetching auth token:', error)
        commit('setToken', null)
        return null
      }
    }
  },
  getters: {
    organizationId: (state) => state.user?.organizationId,
    name: (state) => state.user?.username,
    email: (state) => state.user?.email,
    isAuthenticated: state => !!state.user,
    token: state => state.token
  }
}