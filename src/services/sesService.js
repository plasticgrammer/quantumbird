import { apiClient } from './apiClient'

export const checkEmailVerification = async (email) => {
  return apiClient.post('/ses/check', { email })
}

export const verifyEmailAddress = async (email) => {
  return apiClient.post('/ses/verify', { email })
}