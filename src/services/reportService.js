import { lambda } from './awsConfig'

const invokeLambda = async (operation, payload) => {
  const params = {
    FunctionName: 'WeeklyReport',
    Payload: JSON.stringify({ operation, payload })
  }

  try {
    const response = await lambda.invoke(params).promise()
    const result = JSON.parse(response.Payload)
    if (result.statusCode >= 400) {
      throw new Error(result.body)
    }
    return result.body
  } catch (error) {
    console.error(`Error in Lambda operation ${operation}:`, error)
    throw error
  }
}

export const submitReport = async (report) => {
  return invokeLambda('create', report)
}

export const updateReport = async (report) => {
  return invokeLambda('update', report)
}

export const deleteReport = async (memberUuid, weekString) => {
  return invokeLambda('delete', { memberUuid, weekString })
}

export const getReport = async (memberUuid, weekString) => {
  return invokeLambda('get', { memberUuid, weekString })
}

export const listReports = async (organizationId, weekString) => {
  return invokeLambda('get', { organizationId, weekString })
}