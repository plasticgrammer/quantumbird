import { callApi } from './apiClient'

const BASE_PATH = '/member'

export const getMember = async (memberUuid) => {
  return callApi('GET', BASE_PATH, null, { memberUuid })
}

export const updateMember = async (member) => {
  return callApi('PUT', BASE_PATH, member)
}

export const getMemberProjects = async (memberUuid) => {
  try {
    const result = await callApi('GET', `${BASE_PATH}/project`, null, { memberUuid })
    return result || []
  } catch (error) {
    console.error('Error fetching member projects:', error)
    throw error
  }
}

export const updateMemberProjects = async (memberUuid, projects) => {
  try {
    await callApi('PUT', BASE_PATH, { memberUuid, projects })
    return true
  } catch (error) {
    console.error('Error updating member projects:', error)
    throw error
  }
}

export const listMembers = async (organizationId) => {
  return callApi('GET', BASE_PATH, null, { organizationId })
}

export const verifyEmail = async (memberUuid) => {
  return callApi('PUT', BASE_PATH, { verifyEmail: true, memberUuid })
}