// services/apiClient.js
import axios from 'axios'

const stage = process.env.STAGE || 'dev'
const API_ENDPOINT = `${process.env.VUE_APP_API_ENDPOINT}/${stage}`

// Create a new instance of axios with a custom config
const api = axios.create({
  baseURL: API_ENDPOINT,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 seconds timeout
})

// Request interceptor for API calls
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for API calls
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      // Implement your token refresh logic here
      // const newToken = await refreshToken()
      // localStorage.setItem('auth_token', newToken)
      // originalRequest.headers['Authorization'] = `Bearer ${newToken}`
      // return api(originalRequest)
    }
    return Promise.reject(error)
  }
)

export const callApi = async (method, path, data = null, queryParams = null, options = {}) => {
  try {
    const config = {
      method,
      url: path,
      ...options,
    }

    if (data) {
      config.data = data
    }

    if (queryParams) {
      config.params = queryParams
    }

    const response = await api(config)
    return response.data
  } catch (error) {
    if (axios.isCancel(error)) {
      console.log('Request canceled:', error.message)
    } else {
      console.error(`Error in API call (${method} ${path}):`, error)
      // You can implement custom error handling here
      // For example, showing a notification to the user
    }
    throw error
  }
}

// Helper function to create a cancelable request
export const createCancelableRequest = (method, path, data = null, queryParams = null, options = {}) => {
  const source = axios.CancelToken.source()
  const promise = callApi(method, path, data, queryParams, { ...options, cancelToken: source.token })
  return { promise, cancel: () => source.cancel('Request canceled by the user') }
}

// Example of a function with retry logic
export const callApiWithRetry = async (method, path, data = null, queryParams = null, options = {}, maxRetries = 3) => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await callApi(method, path, data, queryParams, options)
    } catch (error) {
      if (i === maxRetries - 1) throw error
      // Wait for 2^i * 1000 milliseconds before retrying
      await new Promise(resolve => setTimeout(resolve, Math.pow(2, i) * 1000))
    }
  }
}