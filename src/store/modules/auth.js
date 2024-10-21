import { fetchUserAttributes, fetchAuthSession, signOut, updateUserAttributes, deleteUser } from 'aws-amplify/auth'
import { termsOfServiceVersion, privacyPolicyVersion } from '@/config/environment'

const USER_CACHE_DURATION = 5 * 60 * 1000 // 5分

export default {
  namespaced: true,
  state: () => ({
    user: null,
    token: null,
    lastTokenFetch: null,
    lastUserFetch: null,
    cognitoUserSub: null
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
    setCognitoUserSub(state, sub) {
      state.cognitoUserSub = sub
    },
    clearAuthState(state) {
      state.user = null
      state.token = null
      state.lastTokenFetch = null
      state.lastUserFetch = null
      state.cognitoUserSub = null
    },
    updateUserPolicyVersions(state, { tosVersion, privacyPolicyVersion }) {
      if (state.user) {
        state.user.tosVersion = tosVersion || state.user.tosVersion
        state.user.privacyPolicyVersion = privacyPolicyVersion || state.user.privacyPolicyVersion
      }
    }
  },
  actions: {
    async fetchUser({ commit, state }) {
      if (state.user && Date.now() - state.lastUserFetch < USER_CACHE_DURATION) {
        return state.user
      }
      try {
        const attributes = await fetchUserAttributes()
        const userInfo = {
          organizationId: attributes['custom:organizationId'],
          username: attributes.name,
          email: attributes.email,
          tosVersion: attributes['custom:tos_version'],
          privacyPolicyVersion: attributes['custom:pp_version']
        }
        commit('setUser', userInfo)
        commit('setCognitoUserSub', attributes.sub)
        return userInfo
      } catch (error) {
        console.error('Error fetching user:', error)
        commit('setUser', null)
        commit('setCognitoUserSub', null)
        throw error
      }
    },

    async fetchAuthToken({ commit, dispatch }, { forceRefresh = false } = {}) {
      try {
        const { tokens } = await fetchAuthSession({ forceRefresh })
        if (tokens?.idToken) {
          const token = tokens.idToken.toString()
          commit('setToken', token)
          return token
        }
        throw new Error('No ID token found in auth session')
      } catch (error) {
        console.error('Error fetching auth token:', error)
        await dispatch('handleAuthFailure')
        throw error
      }
    },

    async handleAuthFailure({ dispatch }) {
      console.log('Authentication failure, signing out...')
      await dispatch('signOut')
      // this.$router.push('/signin')
      // このアクションを呼び出す側でリダイレクトを処理するべきです
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
        throw error // エラーを上位に伝播させる
      }
    },

    async deleteUserAccount({ commit }) {
      try {
        // ユーザーアカウントを削除
        await deleteUser()

        // ローカルの認証状態をクリア
        commit('clearAuthState')

        return { success: true, message: 'アカウントが正常に削除されました' }
      } catch (error) {
        console.error('Error deleting user account:', error)
        console.error('Error details:', JSON.stringify(error, Object.getOwnPropertyNames(error)))

        let errorMessage = 'アカウントの削除中にエラーが発生しました'
        if (error.name === 'NotAuthorizedException') {
          errorMessage = '認証エラー：再度ログインしてから試してください'
        } else if (error.name === 'LimitExceededException') {
          errorMessage = 'しばらく時間をおいてから再度お試しください'
        }

        throw new Error(errorMessage)
      }
    },

    async checkPolicyAcceptance({ state, dispatch }) {
      const user = state.user || await dispatch('fetchUser')

      return {
        needsTosAcceptance: user.tosVersion !== termsOfServiceVersion,
        needsPrivacyPolicyAcceptance: user.privacyPolicyVersion !== privacyPolicyVersion
      }
    },

    async updatePolicyAcceptance({ commit, dispatch }, { tosAccepted, privacyPolicyAccepted }) {
      try {
        console.log('Updating policy acceptance:', { tosAccepted, privacyPolicyAccepted })
        console.log('Current versions:', { termsOfServiceVersion, privacyPolicyVersion })

        const updates = {}
        let hasUpdates = false

        if (tosAccepted && termsOfServiceVersion) {
          updates['custom:tos_version'] = termsOfServiceVersion
          hasUpdates = true
        }
        if (privacyPolicyAccepted && privacyPolicyVersion) {
          updates['custom:pp_version'] = privacyPolicyVersion
          hasUpdates = true
        }

        console.log('Attributes to update:', updates)

        if (hasUpdates) {
          console.log('Calling updateUserAttributes with:', updates)
          const result = await updateUserAttributes({
            userAttributes: updates
          })
          console.log('updateUserAttributes result:', result)

          commit('updateUserPolicyVersions', {
            tosVersion: tosAccepted ? termsOfServiceVersion : undefined,
            privacyPolicyVersion: privacyPolicyAccepted ? privacyPolicyVersion : undefined
          })

          // ユーザー情報を再取得してキャッシュを更新
          await dispatch('fetchUser')
        } else {
          console.log('No updates to policy acceptance were necessary')
        }

        return { success: true }
      } catch (error) {
        console.error('Error updating policy acceptance:', error)
        console.error('Error details:', JSON.stringify(error, Object.getOwnPropertyNames(error)))
        throw error
      }
    }
  },

  getters: {
    organizationId: (state) => state.user?.organizationId,
    name: (state) => state.user?.username,
    email: (state) => state.user?.email,
    isAuthenticated: state => !!state.user,
    token: state => state.token,
    cognitoUserSub: state => state.cognitoUserSub,
    tosVersion: state => state.user?.tosVersion,
    privacyPolicyVersion: state => state.user?.privacyPolicyVersion
  }
}