import { callApi } from './apiClient'

export const checkEmailVerification = async (email) => {
  return callApi('POST', '/ses/check', { email })
}

export const verifyEmailAddress = async (email) => {
  return callApi('POST', '/ses/verify', { email })
}