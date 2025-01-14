import { apiClient } from './apiClient'

const BASE_PATH = '/weekly-report'

export const submitReport = async (report) => {
  return apiClient.post(BASE_PATH, report)
}

export const updateReport = async (report) => {
  return apiClient.put(BASE_PATH, report)
}

export const deleteReport = async (memberUuid, weekString) => {
  return apiClient.delete(BASE_PATH, { memberUuid, weekString })
}

export const getReport = async (memberUuid, weekString) => {
  return apiClient.get(BASE_PATH, { memberUuid, weekString })
}

export const listReports = async (params) => {
  return apiClient.get(BASE_PATH, params)
}

export const listMemberReports = async (memberUuid) => {
  return apiClient.get(`${BASE_PATH}/member/${memberUuid}`)
}

export const exportReports = async (organizationId) => {
  return apiClient.get(`${BASE_PATH}/export`, { organizationId })
}

export const getReportStatus = async (organizationId, weekString) => {
  return apiClient.get(`${BASE_PATH}/status`, { organizationId, weekString })
}

export const getStatsData = async (organizationId) => {
  return apiClient.get(`${BASE_PATH}/stats`, { organizationId })
}

export const submitFeedback = async (memberUuid, weekString, feedback) => {
  return apiClient.post(`${BASE_PATH}/feedback`, { memberUuid, weekString, feedback })
}