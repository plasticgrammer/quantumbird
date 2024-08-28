// services/apiClient.js
import axios from 'axios'
import store from '@/store'

const stage = process.env.STAGE || 'dev'
const API_ENDPOINT = `${process.env.VUE_APP_API_ENDPOINT}/${stage}`

// Create a new instance of axios with a custom config
const api = axios.create({
  baseURL: API_ENDPOINT,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 seconds timeout
  withCredentials: false
})

// Request interceptor for API calls
api.interceptors.request.use(
  (config) => {
    const token = store.getters['auth/token']
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    console.error('Request interceptor error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor for API calls
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      try {
        // Implement your token refresh logic here
        // const newToken = await refreshToken()
        // store.commit('auth/setToken', newToken)
        // originalRequest.headers['Authorization'] = `Bearer ${newToken}`
        // return api(originalRequest)
      } catch (refreshError) {
        console.error('Token refresh failed:', refreshError)
        // Redirect to login or handle authentication failure
        store.dispatch('auth/signOut')
        return Promise.reject(refreshError)
      }
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
      console.error('Error details:', {
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        config: error.config,
      })
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
      console.warn(`API call attempt ${i + 1} failed:`, error)
      if (i === maxRetries - 1) {
        console.error(`All ${maxRetries} attempts failed for API call (${method} ${path})`)
        throw error
      }
      // Wait for 2^i * 1000 milliseconds before retrying
      const delay = Math.pow(2, i) * 1000
      console.log(`Retrying in ${delay}ms...`)
      await new Promise(resolve => setTimeout(resolve, delay))
    }
  }
}

export default {
  get: (path, queryParams, options) => callApi('GET', path, null, queryParams, options),
  post: (path, data, options) => callApi('POST', path, data, null, options),
  put: (path, data, options) => callApi('PUT', path, data, null, options),
  delete: (path, options) => callApi('DELETE', path, null, null, options),
  // Add more methods as needed
}