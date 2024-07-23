import { lambda } from './awsConfig'

const invokeLambda = async (operation, payload) => {
  const params = {
    FunctionName: 'Organization',
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

export const submitOrganization = async (organization) => {
  return invokeLambda('create', organization)
}

export const updateOrganization = async (organization) => {
  return invokeLambda('update', organization)
}

export const deleteOrganization = async (organizationId) => {
  return invokeLambda('delete', { organizationId })
}

export const getOrganization = async (organizationId) => {
  return invokeLambda('get', { organizationId })
}

export const listOrganizations = async () => {
  return invokeLambda('get', {})
}