import { apiClient } from './apiClient'

const BASE_PATH = '/organization'

export const submitOrganization = async (organization) => {
  const orgData = { ...organization }
  delete orgData.members
  return apiClient.post(BASE_PATH, orgData)
}

export const updateOrganization = async (organization) => {
  const orgData = { ...organization }
  delete orgData.members
  return apiClient.put(BASE_PATH, orgData)
}

export const updateOrganizationFeatures = async (organization_id, features) => {
  return apiClient.put(BASE_PATH, {
    organizationId: organization_id,
    features: features
  })
}

export const deleteOrganization = async (organizationId) => {
  return apiClient.delete(BASE_PATH, { organizationId })
}

export const deleteOrganizationCompletely = async (organizationId) => {
  return apiClient.delete(BASE_PATH, { organizationId, mode: 'complete' })
}

export const getOrganization = async (organizationId) => {
  try {
    return await apiClient.get(BASE_PATH, { organizationId })
  } catch (error) {
    if (error.message.includes('not found')) {
      return null // 組織が見つからない場合はnullを返す
    }
    throw error // その他のエラーは上位に伝播させる
  }
}

export const listOrganizations = async () => {
  return apiClient.get(BASE_PATH)
}

export const registerPushSubscription = async (fcmToken, organizationId, adminId) => {
  return apiClient.post(`${BASE_PATH}/push-subscription`, { fcmToken, organizationId, adminId })
}

export const removePushSubscription = async (organizationId, adminId) => {
  return apiClient.delete(`${BASE_PATH}/push-subscription`, { organizationId, adminId })
}

export const getPushSubscription = async (organizationId, adminId) => {
  const response = await apiClient.get(`${BASE_PATH}/push-subscription`, { organizationId, adminId })
  return response.endpointArn
}