import { apiClient } from './apiClient'

export const generateToken = async (params) => {
  return apiClient.post('/secure/generate', params)
}

export const verifyToken = async (token) => {
  return apiClient.post('/secure/verify', { token })
}