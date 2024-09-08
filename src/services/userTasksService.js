import { apiClient } from './apiClient'

const BASE_PATH = '/user-tasks'

export const submitUserTasks = async (userTasks) => {
  return apiClient.post(BASE_PATH, userTasks)
}

export const updateUserTasks = async (userTasks) => {
  return apiClient.put(BASE_PATH, userTasks)
}

export const deleteUserTasks = async (userId, taskId) => {
  return apiClient.delete(BASE_PATH, { userId, taskId })
}

export const getUserTasks = async (userId, taskId) => {
  try {
    return await apiClient.get(BASE_PATH, { userId, taskId })
  } catch (error) {
    return null // 組織が見つからない場合はnullを返す
  }
}

export const listUserTasks = async (userId) => {
  return apiClient.get(BASE_PATH, { userId })
}