import { apiClient } from './apiClient'

const BASE_PATH = '/payment'

export const createSubscription = async (subscriptionData) => {
  return apiClient.post(`${BASE_PATH}/create-subscription`, subscriptionData)
}

export const updateSubscription = async (updateData) => {
  return apiClient.post(`${BASE_PATH}/update-subscription`, updateData)
}

export const changePlan = async (changeData) => {
  const response = await apiClient.post(`${BASE_PATH}/change-plan`, changeData)

  // フリープランへの変更時の特別処理
  if (response.subscription?.status === 'canceled' && response.subscription?.currentPeriodEnd) {
    response.message = `次回支払い日（${new Date(response.subscription.currentPeriodEnd * 1000).toLocaleDateString()}）でフリープランに変更されます`
  }

  return response
}

export const getPaymentMethods = async (email) => {
  const response = await apiClient.post(`${BASE_PATH}/payment-methods`, { email })
  return response
}

export const updatePaymentMethod = async (updateData) => {
  const response = await apiClient.post(`${BASE_PATH}/update-payment-method`, updateData)
  return response
}

export const getInvoices = async (customerId) => {
  const response = await apiClient.post(`${BASE_PATH}/invoices`, { customerId })
  return response
}

export const getSubscriptionInfo = async (customerId) => {
  const response = await apiClient.post(`${BASE_PATH}/subscription-info`, { customerId })
  return response
}
