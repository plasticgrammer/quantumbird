import { apiClient } from './apiClient'

const BASE_PATH = '/public'

export const getReport = async (memberUuid, weekString) => {
  return apiClient.get(`${BASE_PATH}/weekly-report`, { memberUuid, weekString })
}

export const submitReport = async (report) => {
  return apiClient.post(`${BASE_PATH}/weekly-report`, report)
}

export const listReports = async (organizationId, weekString) => {
  return apiClient.get(`${BASE_PATH}/weekly-report`, { organizationId, weekString })
}

export const listMembers = async (organizationId) => {
  return apiClient.get(`${BASE_PATH}/member`, { organizationId })
}

export const getMemberProjects = async (memberUuid) => {
  try {
    const result = await apiClient.get(`${BASE_PATH}/project`, { memberUuid })
    return result || []
  } catch (error) {
    console.error('Error fetching member projects:', error)
    throw error
  }
}

export const updateMemberProjects = async (memberUuid, projects) => {
  try {
    await apiClient.put(`${BASE_PATH}/member`, { memberUuid, projects })
    return true
  } catch (error) {
    console.error('Error updating member projects:', error)
    throw error
  }
}
