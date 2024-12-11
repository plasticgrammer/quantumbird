import { apiClient } from './apiClient'

const BASE_PATH = '/member'

export const getMember = async (memberUuid) => {
  return apiClient.get(BASE_PATH, { memberUuid })
}

export const updateMember = async (member) => {
  return apiClient.put(BASE_PATH, member)
}

export const getMemberProjects = async (memberUuid) => {
  const result = await apiClient.get(`${BASE_PATH}/project`, { memberUuid })
  return result || []
}

export const updateMemberProjects = async (memberUuid, projects) => {
  await apiClient.put(BASE_PATH, { memberUuid, projects })
  return true
}

export const listMembers = async (organizationId) => {
  return apiClient.get(BASE_PATH, { organizationId })
}

export const verifyEmail = async (memberUuid) => {
  return apiClient.put(`${BASE_PATH}/mail`, { verifyEmail: true, memberUuid })
}