import { lambda } from './awsConfig'

const invokeLambda = async (operation, payload) => {
  const params = {
    FunctionName: 'Organizations',
    Payload: JSON.stringify({ operation, payload })
  }

  try {
    const response = await lambda.invoke(params).promise()
    const result = JSON.parse(response.Payload)
    if (result.statusCode >= 400) {
      throw new Error(result.body)
    }
    return JSON.parse(result.body)
  } catch (error) {
    console.error(`Error in Lambda operation ${operation}:`, error)
    throw error
  }
}

export const submitOrganization = async (report) => {
  return invokeLambda('create', report)
}

export const updateOrganization = async (report) => {
  return invokeLambda('update', report)
}

export const deleteOrganization = async (memberUuid, weekString) => {
  return invokeLambda('delete', { memberUuid, weekString })
}

export const getOrganization = async (memberUuid, weekString) => {
  return invokeLambda('get', { memberUuid, weekString })
}

export const listOrganizations = async (organizationId, weekString) => {
  return invokeLambda('get', { organizationId, weekString })
}