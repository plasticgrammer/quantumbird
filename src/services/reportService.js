import { callApi } from './apiClient'

const BASE_PATH = '/weekly-report'

export const submitReport = async (report) => {
  return callApi('POST', BASE_PATH, report)
}

export const updateReport = async (report) => {
  return callApi('PUT', BASE_PATH, report)
}

export const deleteReport = async (memberUuid, weekString) => {
  return callApi('DELETE', BASE_PATH, null, { memberUuid, weekString })
}

export const getReport = async (memberUuid, weekString) => {
  return callApi('GET', BASE_PATH, null, { memberUuid, weekString })
}

export const listReports = async (organizationId, weekString) => {
  return callApi('GET', BASE_PATH, null, { organizationId, weekString })
}

export const getReportStatus = async (organizationId, weekString) => {
  return callApi('GET', `${BASE_PATH}/status`, null, { organizationId, weekString })
}

export const getStatsData = async (organizationId) => {
  return callApi('GET', `${BASE_PATH}/stats`, null, { organizationId })
}

export const submitFeedback = async (memberUuid, weekString, feedback) => {
  return callApi('POST', `${BASE_PATH}/feedback`, { memberUuid, weekString, feedback })
}