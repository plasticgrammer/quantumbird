import { callApi } from './apiClient'

const BASE_PATH = '/organization'

export const submitOrganization = async (organization) => {
  return callApi('POST', BASE_PATH, organization)
}

export const updateOrganization = async (organization) => {
  return callApi('PUT', BASE_PATH, organization)
}

export const deleteOrganization = async (organizationId) => {
  return callApi('DELETE', BASE_PATH, null, { organizationId })
}

export const getOrganization = async (organizationId) => {
  try {
    return await callApi('GET', BASE_PATH, null, { organizationId })
  } catch (error) {
    if (error.message.includes('not found')) {
      return null // 組織が見つからない場合はnullを返す
    }
    throw error // その他のエラーは上位に伝播させる
  }
}

export const listOrganizations = async () => {
  return callApi('GET', BASE_PATH)
}