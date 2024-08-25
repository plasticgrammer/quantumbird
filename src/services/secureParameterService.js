import axios from 'axios'

const API_ENDPOINT = process.env.VUE_APP_API_ENDPOINT

const apiClient = axios.create({
  baseURL: API_ENDPOINT,
  headers: {
    'Content-Type': 'application/json'
  },
  withCredentials: false // CORSリクエストにクレデンシャルを含めない
})

export const generateToken = async (params) => {
  try {
    const response = await apiClient.post('/secure/generate', params)
    return response.data
  } catch (error) {
    console.error('Error generating token:', error)
    throw error
  }
}

export const verifyToken = async (token) => {
  try {
    const response = await apiClient.post('/secure/verify', { token })
    return response.data
  } catch (error) {
    console.error('Error verifying token:', error)
    throw error
  }
}