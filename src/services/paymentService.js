import { apiClient } from './apiClient'

const BASE_PATH = '/payment'

export const createSubscription = async (subscriptionData) => {
  return apiClient.post(`${BASE_PATH}/create-subscription`, subscriptionData)
}

export const updateSubscription = async (updateData) => {
  return apiClient.post(`${BASE_PATH}/update-subscription`, updateData)
}

export const changePlan = async (changeData) => {
  return apiClient.post(`${BASE_PATH}/change-plan`, changeData)
}

export const getPaymentMethods = async (email) => {
  return apiClient.post(`${BASE_PATH}/payment-methods`, { email })
}

export const updatePaymentMethod = async (updateData) => {
  return apiClient.post(`${BASE_PATH}/update-payment-method`, updateData)
}
