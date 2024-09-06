import axios from 'axios'
import store from '@/store'

const stage = process.env.STAGE || 'dev'
const API_ENDPOINT = `${process.env.VUE_APP_API_ENDPOINT}/${stage}`

const api = axios.create({
  baseURL: API_ENDPOINT,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
  withCredentials: false
})

let activeRequests = 0
let loadingTimeout = null
const LOADING_DELAY = 300 // 300ms delay before showing loading

const startLoading = () => {
  activeRequests++
  if (loadingTimeout === null) {
    loadingTimeout = setTimeout(() => {
      store.dispatch('setLoading', true)
    }, LOADING_DELAY)
  }
}

const stopLoading = () => {
  activeRequests--
  if (activeRequests === 0) {
    clearTimeout(loadingTimeout)
    loadingTimeout = null
    store.dispatch('setLoading', false)
  }
}

// Request interceptor
api.interceptors.request.use(
  (config) => {
    startLoading()
    const token = store.getters['auth/token']
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    stopLoading()
    console.error('Request interceptor error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    stopLoading()
    return response
  },
  async (error) => {
    stopLoading()
    const originalRequest = error.config
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      try {
        const newToken = await store.dispatch('auth/fetchAuthToken')
        originalRequest.headers['Authorization'] = `Bearer ${newToken}`
        return api(originalRequest)
      } catch (refreshError) {
        console.error('Token refresh failed:', refreshError)
        store.dispatch('auth/signOut')
        return Promise.reject(refreshError)
      }
    }
    console.error(`Error in API call (${originalRequest.method} ${originalRequest.url}):`, error)
    console.error('Error details:', {
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      config: error.config,
    })
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
      // Error is already logged in the response interceptor
      // You can implement additional custom error handling here if needed
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

export const apiClient = {
  get: (path, queryParams, options) => callApi('GET', path, null, queryParams, options),
  post: (path, data, options) => callApi('POST', path, data, null, options),
  put: (path, data, options) => callApi('PUT', path, data, null, options),
  delete: (path, queryParams, options) => callApi('DELETE', path, null, queryParams, options),
  // Add more methods as needed
}