import { callApi } from './apiClient'

export const generateToken = async (params) => {
  return callApi('POST', '/secure/generate', params)
}

export const verifyToken = async (token) => {
  return callApi('POST', '/secure/verify', { token })
}