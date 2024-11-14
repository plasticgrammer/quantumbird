import axios from 'axios'
import store from '@/store'

const stage = process.env.VUE_APP_STAGE || 'dev'
const API_ENDPOINT = `${process.env.VUE_APP_API_ENDPOINT}/${stage}`
const LOADING_DELAY = 600 // ms delay before showing loading

const api = axios.create({
  baseURL: API_ENDPOINT,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
  withCredentials: false
})

let activeRequests = 0
let loadingTimeout = null
let isRefreshing = false
let failedQueue = []

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

const ERROR_TYPES = {
  CORS: 'CORS_ERROR',
  NETWORK: 'NETWORK_ERROR',
  AUTH: 'AUTH_ERROR',
  UNKNOWN: 'UNKNOWN_ERROR'
}

const getErrorType = (error) => {
  if (error.code === 'ERR_NETWORK' && !error.response) {
    // CORSエラーの特徴的なパターンをチェック
    const isCORS = error.message.includes('CORS') ||
      error.message.includes('Network Error') ||
      error.message.includes('cross-origin')
    return isCORS ? ERROR_TYPES.CORS : ERROR_TYPES.NETWORK
  }
  if (error.response?.status === 401) {
    return ERROR_TYPES.AUTH
  }
  return ERROR_TYPES.UNKNOWN
}

// 変数名を変更し、実際に使用されていることを明確にする
const checkTokenError = (error) => {
  const errorType = getErrorType(error)

  // デバッグ用の詳細なログ出力
  console.error('Error details:', {
    type: errorType,
    code: error.code,
    message: error.message,
    response: error.response,
    isAxiosError: error.isAxiosError,
    config: error.config
  })

  // 認証エラーの場合のみtrueを返す
  return errorType === ERROR_TYPES.AUTH
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

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  failedQueue = []
}

// Response interceptor
api.interceptors.response.use(
  (response) => {
    stopLoading()
    return response
  },
  async (error) => {
    stopLoading()
    const originalRequest = error.config
    const errorType = getErrorType(error)

    // CORSエラーの場合、即時リトライ
    if (errorType === ERROR_TYPES.CORS && !originalRequest._corsRetry) {
      originalRequest._corsRetry = true
      console.log('Retrying CORS error request with new token...')
      // 新しいトークンを取得して即時リトライ
      try {
        const newToken = await store.dispatch('auth/fetchAuthToken')
        originalRequest.headers['Authorization'] = `Bearer ${newToken}`
        return api(originalRequest)
      } catch (refreshError) {
        console.error('Token refresh failed during CORS retry:', refreshError)
        await store.dispatch('auth/signOut')
        return Promise.reject(refreshError)
      }
    }

    // 認証エラーの場合の処理
    if (checkTokenError(error) && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        }).then(token => {
          originalRequest.headers['Authorization'] = `Bearer ${token}`
          return api(originalRequest)
        }).catch(err => Promise.reject(err))
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        const newToken = await store.dispatch('auth/fetchAuthToken')
        processQueue(null, newToken)
        originalRequest.headers['Authorization'] = `Bearer ${newToken}`
        return api(originalRequest)
      } catch (refreshError) {
        processQueue(refreshError, null)
        console.error('Token refresh failed:', refreshError)
        await store.dispatch('auth/signOut')
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    // 通常のネットワークエラーの場合
    if (errorType === ERROR_TYPES.NETWORK && !originalRequest._networkRetry) {
      originalRequest._networkRetry = true
      console.log('Retrying network request...')
      const currentToken = store.getters['auth/token']
      if (currentToken) {
        originalRequest.headers['Authorization'] = `Bearer ${currentToken}`
      }
      return new Promise(resolve => setTimeout(resolve, 1000))
        .then(() => api(originalRequest))
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

const handleError = (error) => {
  if (error.response) {
    // サーバーからのレスポンスにエラーが含まれている場合
    const errorMessage = error.response.data.error || error.response.data.message || 'エラーが発生しました'
    throw new Error(errorMessage)
  }
  throw error
}

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
    }
    throw handleError(error)
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
}