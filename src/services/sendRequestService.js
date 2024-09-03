import { apiClient } from './apiClient'

export const sendRequest = async (organizationId, weekString) => {
  return apiClient.post('/send-request', { organizationId, weekString })
}
