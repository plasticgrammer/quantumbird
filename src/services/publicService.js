import { apiClient } from './apiClient'

const BASE_PATH = '/public'

export const getOrganization = async (organizationId) => {
  try {
    return await apiClient.get(`${BASE_PATH}/organization`, { organizationId })
  } catch (error) {
    if (error.message.includes('not found')) {
      return null
    }
    throw error
  }
}

export const submitOrganization = async (organization) => {
  return apiClient.post(`${BASE_PATH}/organization`, organization)
}

export const getReport = async (memberUuid, weekString) => {
  return apiClient.get(`${BASE_PATH}/weekly-report`, { memberUuid, weekString })
}

export const submitReport = async (report) => {
  return apiClient.post(`${BASE_PATH}/weekly-report`, report)
}

export const updateReport = async (report) => {
  return apiClient.put(`${BASE_PATH}/weekly-report`, report)
}

export const listReports = async (organizationId, weekString) => {
  return apiClient.get(`${BASE_PATH}/weekly-report`, { organizationId, weekString })
}

export const listMembers = async (organizationId) => {
  return apiClient.get(`${BASE_PATH}/member`, { organizationId })
}

export const getMember = async (memberUuid) => {
  return apiClient.get(`${BASE_PATH}/member`, { memberUuid })
}

export const getMemberProjects = async (memberUuid) => {
  const result = await apiClient.get(`${BASE_PATH}/project`, { memberUuid })
  return result || []
}

export const updateMemberExtraInfo = async (memberUuid, extraInfo) => {
  await apiClient.put(`${BASE_PATH}/member`, { memberUuid, extraInfo })
  return true
}

export const updateMemberProjects = async (memberUuid, projects) => {
  await apiClient.put(`${BASE_PATH}/member`, { memberUuid, projects })
  return true
}
