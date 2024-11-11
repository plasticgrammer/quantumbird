import { fetchUserAttributes, fetchAuthSession, signOut, updateUserAttributes, updatePassword, deleteUser } from 'aws-amplify/auth'
import { termsOfServiceVersion, privacyPolicyVersion } from '@/config/environment'

const AUTH_CONSTANTS = {
  CACHE_DURATION: 5 * 60 * 1000, // 5分
  ERROR_MESSAGES: {
    AUTH: '認証エラー：再度ログインしてから試してください',
    RATE_LIMIT: 'しばらく時間をおいてから再度お試しください',
    GENERIC: 'エラーが発生しました',
    DELETE_ACCOUNT: 'アカウントの削除中にエラーが発生しました',
    NO_TOKEN: '認証情報が見つかりません。再度ログインしてください',
    SUBSCRIPTION_UPDATE: 'サブスクリプション情報の更新権限がありません。管理者に連絡してください'
  }
}

const createErrorHandler = (prefix) => (error) => {
  console.error(`Error ${prefix}:`, error)
  if (error?.details) {
    console.error('Error details:', JSON.stringify(error, Object.getOwnPropertyNames(error)))
  }
  throw error
}

const mapErrorMessage = (error) => {
  if (error.name === 'NotAuthorizedException') {
    return error.message.includes('unauthorized attribute')
      ? AUTH_CONSTANTS.ERROR_MESSAGES.SUBSCRIPTION_UPDATE
      : AUTH_CONSTANTS.ERROR_MESSAGES.AUTH
  }
  if (error.name === 'LimitExceededException') {
    return AUTH_CONSTANTS.ERROR_MESSAGES.RATE_LIMIT
  }
  return error.message || AUTH_CONSTANTS.ERROR_MESSAGES.GENERIC
}

export default {
  namespaced: true,

  state: () => ({
    user: null,
    token: null,
    lastTokenFetch: null,
    lastUserFetch: null,
    cognitoUserSub: null,
    subscription: {
      planId: null,
      accountCount: 0,
      subscriptionId: null
    }
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
      Object.assign(state, {
        user: null,
        token: null,
        lastTokenFetch: null,
        lastUserFetch: null,
        cognitoUserSub: null,
        subscription: {
          planId: null,
          accountCount: 0,
          subscriptionId: null
        }
      })
    },

    updateUserPolicyVersions(state, { tosVersion, privacyPolicyVersion }) {
      if (state.user) {
        Object.assign(state.user, {
          tosVersion: tosVersion || state.user.tosVersion,
          privacyPolicyVersion: privacyPolicyVersion || state.user.privacyPolicyVersion
        })
      }
    },

    setSubscription(state, { planId, accountCount, subscriptionId }) {
      Object.assign(state.subscription, {
        planId,
        accountCount: parseInt(accountCount || '0', 10),
        subscriptionId: subscriptionId || null
      })
      // ユーザー情報にも同期
      if (state.user) {
        Object.assign(state.user.subscription, { ...state.subscription })
      }
    }
  },

  actions: {
    async fetchUser({ commit, state, dispatch }) {
      try {
        if (state.user && Date.now() - state.lastUserFetch < AUTH_CONSTANTS.CACHE_DURATION) {
          // キャッシュ期間内の場合、トークンの有効性を確認
          await dispatch('validateToken')
          return state.user
        }

        const attributes = await fetchUserAttributes()
        const userInfo = {
          organizationId: attributes['custom:organizationId'],
          username: attributes.name,
          email: attributes.email,
          tosVersion: attributes['custom:tos_version'],
          privacyPolicyVersion: attributes['custom:pp_version'],
          subscription: {
            planId: attributes['custom:planId'] || 'free',
            accountCount: parseInt(attributes['custom:accountCount'] || '0', 10),
            subscriptionId: attributes['custom:subscriptionId'] || null
          }
        }

        commit('setUser', userInfo)
        commit('setCognitoUserSub', attributes.sub)
        commit('setSubscription', userInfo.subscription)
        return userInfo
      } catch (error) {
        createErrorHandler('fetching user')(error)
        commit('setUser', null)
        commit('setCognitoUserSub', null)
        throw error
      }
    },

    async fetchAuthToken({ commit, dispatch }, { forceRefresh = false } = {}) {
      try {
        const { tokens } = await fetchAuthSession({ forceRefresh })
        if (!tokens?.idToken) {
          throw new Error(AUTH_CONSTANTS.ERROR_MESSAGES.NO_TOKEN)
        }

        const token = tokens.idToken.toString()
        commit('setToken', token)
        return token
      } catch (error) {
        createErrorHandler('fetching auth token')(error)

        // トークンのリフレッシュを試行
        try {
          const { tokens } = await fetchAuthSession({ forceRefresh: true })
          if (!tokens?.idToken) {
            throw new Error(AUTH_CONSTANTS.ERROR_MESSAGES.NO_TOKEN)
          }

          const token = tokens.idToken.toString()
          commit('setToken', token)
          return token
        } catch (refreshError) {
          createErrorHandler('refreshing auth token')(refreshError)
          await dispatch('handleAuthFailure')
          throw refreshError
        }
      }
    },

    async validateToken({ dispatch }) {
      try {
        // トークンの有効性を確認
        await fetchAuthSession()
      } catch (error) {
        createErrorHandler('validating token')(error)

        // トークンが無効な場合、再取得を試行
        await dispatch('fetchAuthToken', { forceRefresh: true })
      }
    },

    async handleAuthFailure({ dispatch }) {
      console.log('Authentication failure, signing out...')
      await dispatch('signOut')
    },

    async signOut({ commit }) {
      try {
        await signOut()
        commit('clearAuthState')
      } catch (error) {
        createErrorHandler('signing out')(error)
        commit('clearAuthState')
        throw error
      }
    },

    async updatePassword(_, { oldPassword, newPassword }) {
      try {
        await updatePassword({ oldPassword, newPassword })
        return { success: true }
      } catch (error) {
        createErrorHandler('updating password')(error)
        throw new Error(mapErrorMessage(error))
      }
    },

    async deleteUserAccount({ commit }) {
      try {
        await deleteUser()
        commit('clearAuthState')
        return { success: true, message: 'アカウントが正常に削除されました' }
      } catch (error) {
        createErrorHandler('deleting user account')(error)
        throw new Error(mapErrorMessage(error))
      }
    },

    async checkPolicyAcceptance({ state, dispatch }) {
      const user = state.user || await dispatch('fetchUser')
      return {
        needsTosAcceptance: user.tosVersion !== termsOfServiceVersion,
        needsPrivacyPolicyAcceptance: user.privacyPolicyVersion !== privacyPolicyVersion
      }
    },

    async updatePolicyAcceptance({ commit }, { tosAccepted, privacyPolicyAccepted }) {
      try {
        const updates = {}

        if (tosAccepted && termsOfServiceVersion) {
          updates['custom:tos_version'] = termsOfServiceVersion
        }
        if (privacyPolicyAccepted && privacyPolicyVersion) {
          updates['custom:pp_version'] = privacyPolicyVersion
        }

        if (Object.keys(updates).length > 0) {
          await updateUserAttributes({ userAttributes: updates })

          commit('updateUserPolicyVersions', {
            tosVersion: tosAccepted ? termsOfServiceVersion : undefined,
            privacyPolicyVersion: privacyPolicyAccepted ? privacyPolicyVersion : undefined
          })
        }

        return { success: true }
      } catch (error) {
        createErrorHandler('updating policy acceptance')(error)
        throw error
      }
    },

    async updateSubscriptionAttributes({ commit }, { planId, accountCount, subscriptionId }) {
      try {
        const updates = {
          'custom:planId': planId,
          'custom:accountCount': String(accountCount),
          'custom:subscriptionId': subscriptionId || ''
        }

        await updateUserAttributes({
          userAttributes: updates
        })

        // 即座にステートを更新
        commit('setSubscription', {
          planId,
          accountCount,
          subscriptionId
        })

        return { success: true }
      } catch (error) {
        createErrorHandler('updating subscription attributes')(error)
        throw new Error(mapErrorMessage(error))
      }
    }
  },

  getters: {
    organizationId: state => state.user?.organizationId,
    name: state => state.user?.username,
    email: state => state.user?.email,
    isAuthenticated: state => !!state.user,
    token: state => state.token,
    cognitoUserSub: state => state.cognitoUserSub,
    tosVersion: state => state.user?.tosVersion,
    privacyPolicyVersion: state => state.user?.privacyPolicyVersion,
    currentSubscription: state => state.subscription || { planId: 'free', accountCount: 0 }
  }
}