
import { apiClient } from './apiClient'

const BASE_PATH = '/account'

export const createAccount = async (account) => {
  return apiClient.post(BASE_PATH, account)
}

export const updateAccount = async (account) => {
  return apiClient.put(BASE_PATH, account)
}

export const deleteAccount = async (organizationId) => {
  return apiClient.delete(BASE_PATH, { organizationId })
}

export const getAccount = async (organizationId) => {
  try {
    return await apiClient.get(BASE_PATH, { organizationId })
  } catch (error) {
    if (error.message.includes('not found')) {
      return null // アカウントが見つからない場合はnullを返す
    }
    throw error // その他のエラーは上位に伝播させる
  }
}

export const getAccounts = async () => {
  return apiClient.get(BASE_PATH)
}

export const resendInvitation = async (email) => {
  return apiClient.post(`${BASE_PATH}/resend-invitation`, { email })
}