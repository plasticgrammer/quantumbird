import { fetchUserAttributes, fetchAuthSession, signOut, updateUserAttributes, updatePassword, deleteUser } from 'aws-amplify/auth'
import { termsOfServiceVersion, privacyPolicyVersion } from '@/config/environment'
import { getSubscriptionInfo } from '@/services/paymentService'

const AUTH_CONSTANTS = {
  CACHE_DURATION: 5 * 60 * 1000, // 5分
  ERROR_MESSAGES: {
    AUTH: '認証エラー：再度ログインしてから試してください',
    RATE_LIMIT: 'しばらく時間をおいてから再度お試しください',
    GENERIC: 'エラーが発生しました',
    DELETE_ACCOUNT: 'アカウントの削除中にエラーが発生しました',
    NO_TOKEN: '認証情報が見つかりません。再度ログインしてください',
    SUBSCRIPTION_UPDATE: 'サブスクリプション情報の更新権限がありません。管理者に連絡してください',
    TEMP_PASSWORD: '初回ログインのため、パスワードの変更が必要です',
    PASSWORD_RESET: 'パスワードのリセットが必要です',
    PASSWORD_CHANGE_REQUIRED: '仮パスワードでのログインのため、パスワードの変更が必要です'
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
  const errorMap = {
    NotAuthorizedException: (msg) =>
      msg.includes('unauthorized attribute')
        ? AUTH_CONSTANTS.ERROR_MESSAGES.SUBSCRIPTION_UPDATE
        : AUTH_CONSTANTS.ERROR_MESSAGES.AUTH,
    LimitExceededException: () => AUTH_CONSTANTS.ERROR_MESSAGES.RATE_LIMIT,
    UserNotConfirmedException: () => 'メールアドレスの確認が完了していません。',
    UserNotFoundException: () => 'このメールアドレスに対応するアカウントが見つかりません。',
    InvalidParameterException: () => '入力内容が正しくありません。',
    default: (msg) => msg || AUTH_CONSTANTS.ERROR_MESSAGES.GENERIC
  }

  return (errorMap[error.name] || errorMap.default)(error.message)
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
      subscriptionId: null,
      stripeCustomerId: null
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
          subscriptionId: null,
          stripeCustomerId: null
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

    setSubscription(state, { planId, priceId, accountCount, subscriptionId, stripeCustomerId }) {
      const subscription = {
        planId,
        priceId,
        accountCount: parseInt(accountCount || '0', 10),
        subscriptionId: subscriptionId || null,
        stripeCustomerId: stripeCustomerId || null
      }
      state.subscription = subscription
    }
  },

  actions: {
    async fetchUser({ commit, state, dispatch }) {
      try {
        // キャッシュチェック
        if (state.user && Date.now() - state.lastUserFetch < AUTH_CONSTANTS.CACHE_DURATION) {
          const isValid = await dispatch('validateToken').catch(() => false)
          if (isValid) return state.user
        }

        const attributes = await fetchUserAttributes()
        const session = await fetchAuthSession()

        // セッション状態の確認
        if (session.challengeName === 'NEW_PASSWORD_REQUIRED') {
          throw new Error(AUTH_CONSTANTS.ERROR_MESSAGES.PASSWORD_CHANGE_REQUIRED)
        }

        // ユーザー情報の設定
        const userInfo = {
          organizationId: attributes['custom:organizationId'],
          username: attributes.name,
          email: attributes.email,
          tosVersion: attributes['custom:tos_version'],
          privacyPolicyVersion: attributes['custom:pp_version'],
          stripeCustomerId: attributes['custom:stripeCustomerId']
        }

        commit('setUser', userInfo)
        commit('setCognitoUserSub', attributes.sub)

        // サブスクリプション情報の取得
        if (attributes['custom:stripeCustomerId']) {
          try {
            const { data } = await dispatch('fetchSubscriptionInfo', attributes['custom:stripeCustomerId'])
            commit('setSubscription', {
              ...data,
              stripeCustomerId: attributes['custom:stripeCustomerId']
            })
          } catch (error) {
            console.error('Subscription fetch error:', error)
          }
        }

        return userInfo

      } catch (error) {
        commit('clearAuthState')
        throw error
      }
    },

    async fetchSubscriptionInfo({ commit }, customerId) {
      try {
        const response = await getSubscriptionInfo(customerId)
        commit('setSubscription', response.data)
        return response
      } catch (error) {
        console.error('Error fetching subscription info:', error)
        throw error
      }
    },

    async fetchAuthToken({ commit, dispatch }, { forceRefresh = false } = {}) {
      try {
        const { tokens } = await fetchAuthSession({ forceRefresh })
        if (!tokens?.idToken) {
          commit('clearAuthState')
          throw new Error(AUTH_CONSTANTS.ERROR_MESSAGES.NO_TOKEN)
        }

        const token = tokens.idToken.toString()
        commit('setToken', token)
        return token
      } catch (error) {
        // 特殊なエラー状態の判定を最初に行う
        if (error.name === 'NewPasswordRequiredException' ||
          error.name === 'PasswordResetRequiredException') {
          // 特殊なエラーの場合は状態をクリアせずにそのまま伝播
          throw error
        }

        console.error('Error fetching auth token:', error)
        commit('clearAuthState')

        // リフレッシュを試みる前に特殊なエラーでないことを確認
        if (!error.message?.includes('needs to be authenticated')) {
          try {
            const { tokens } = await fetchAuthSession({ forceRefresh: true })
            if (tokens?.idToken) {
              const token = tokens.idToken.toString()
              commit('setToken', token)
              return token
            }
          } catch (refreshError) {
            console.error('Token refresh failed:', refreshError)
          }
        }

        await dispatch('handleAuthFailure', { error })
        throw error
      }
    },

    async validateToken({ dispatch, state }) {
      try {
        if (!state.token) {
          return await dispatch('fetchAuthToken', { forceRefresh: true })
        }
        await fetchAuthSession()
        return state.token
      } catch (error) {
        console.error('Token validation failed:', error)
        return await dispatch('fetchAuthToken', { forceRefresh: true })
      }
    },

    async handleAuthFailure({ dispatch }, { error } = {}) {
      // 特殊なエラーの場合は、そのまま上位に伝播
      if (error?.name === 'NewPasswordRequiredException') {
        return Promise.reject(error)
      }
      if (error?.name === 'PasswordResetRequiredException') {
        return Promise.reject(error)
      }

      await dispatch('signOut')
      throw new Error(AUTH_CONSTANTS.ERROR_MESSAGES.AUTH)
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

    async checkPolicyAcceptance({ dispatch }) {
      const user = await dispatch('fetchUser')
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

    async updateSubscriptionAttributes({ commit, dispatch }, { stripeCustomerId }) {
      try {
        await updateUserAttributes({
          userAttributes: {
            'custom:stripeCustomerId': stripeCustomerId || ''
          }
        })

        if (stripeCustomerId) {
          const { data } = await dispatch('fetchSubscriptionInfo', stripeCustomerId)
          commit('setSubscription', {
            ...data,
            stripeCustomerId
          })
        } else {
          commit('setSubscription', {
            planId: 'free',
            accountCount: 0,
            subscriptionId: null,
            stripeCustomerId: null
          })
        }

        return { success: true }
      } catch (error) {
        createErrorHandler('updating subscription info')(error)
        throw new Error(mapErrorMessage(error))
      }
    },

    async completeNewPassword({ dispatch, state }, { newPassword }) {
      try {
        const { confirmSignIn } = await import('@aws-amplify/auth')
        await confirmSignIn({
          challengeResponse: newPassword,
          options: {
            userAttributes: {
              name: state.user?.email || '' // Use email as name if no username is available
            }
          }
        })

        // パスワード変更後に自動的にサインインを完了
        await dispatch('fetchUser')
        return { success: true }
      } catch (error) {
        createErrorHandler('completing new password')(error)
        throw new Error(mapErrorMessage(error))
      }
    },

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