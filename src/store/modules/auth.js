import { fetchUserAttributes, fetchAuthSession } from 'aws-amplify/auth'

export default {
  namespaced: true,
  state: () => ({
    user: null,
    token: null,
    lastTokenFetch: null,
    lastUserFetch: null
  }),
  mutations: {
    setUser(state, user) {
      state.user = user
      state.lastUserFetch = Date.now()
    },
    setToken(state, token) {
      state.token = token
      state.lastTokenFetch = Date.now()
    }
  },
  actions: {
    async fetchUser({ commit, state }) {
      // ユーザー情報のキャッシュ期限を5分とする
      if (state.user && Date.now() - state.lastUserFetch < 5 * 60 * 1000) {
        return state.user
      }
      try {
        const attributes = await fetchUserAttributes()
        const userInfo = {
          organizationId: attributes['custom:organizationId'],
          username: attributes.name,
          email: attributes.email,
        }
        commit('setUser', userInfo)
        return userInfo
      } catch (error) {
        console.error('Error fetching user:', error)
        commit('setUser', null)
        return null
      }
    },
    async fetchAuthToken({ commit, state }) {
      // トークンのキャッシュ期限を55分とする（通常、トークンの有効期限は1時間）
      if (state.token && Date.now() - state.lastTokenFetch < 55 * 60 * 1000) {
        return state.token
      }
      try {
        const { tokens } = await fetchAuthSession()
        if (tokens && tokens.idToken) {
          const token = tokens.idToken.toString()
          commit('setToken', token)
          return token
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