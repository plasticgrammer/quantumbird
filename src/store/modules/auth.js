import { fetchUserAttributes, fetchAuthSession, signOut } from 'aws-amplify/auth'

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
    },
    clearAuthState(state) {
      state.user = null
      state.token = null
      state.lastTokenFetch = null
      state.lastUserFetch = null
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

    async fetchAuthToken({ commit, dispatch, state }) {
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
        // トークンが取得できなかった場合
        await dispatch('handleAuthFailure')
        return null
      } catch (error) {
        console.error('Error fetching auth token:', error)
        await dispatch('handleAuthFailure')
        return null
      }
    },

    async handleAuthFailure({ dispatch }) {
      console.log('Authentication failure, signing out...')
      await dispatch('signOut')
      // ここでルーターを使用してログインページにリダイレクトするなどの処理を追加できます
    },

    async signOut({ commit }) {
      try {
        await signOut()
        commit('clearAuthState')
        console.log('Successfully signed out')
      } catch (error) {
        console.error('Error signing out:', error)
        // エラーが発生しても状態をクリアする
        commit('clearAuthState')
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