import { apiClient } from './apiClient'

const BASE_PATH = '/member'

export const getMember = async (memberUuid) => {
  return apiClient.get(BASE_PATH, { memberUuid })
}

export const updateMember = async (member) => {
  return apiClient.put(BASE_PATH, member)
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
    await apiClient.put(BASE_PATH, { memberUuid, projects })
    return true
  } catch (error) {
    console.error('Error updating member projects:', error)
    throw error
  }
}

export const listMembers = async (organizationId) => {
  return apiClient.get(BASE_PATH, { organizationId })
}

export const verifyEmail = async (memberUuid) => {
  return apiClient.put(`${BASE_PATH}/mail`, { verifyEmail: true, memberUuid })
}