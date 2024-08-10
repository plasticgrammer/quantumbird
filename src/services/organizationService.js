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
    return result.body
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
  try {
    const response = await invokeLambda('get', { organizationId })
    return response
  } catch (error) {
    if (error.message.includes('not found')) {
      return null // 組織が見つからない場合はnullを返す
    }
    throw error // その他のエラーは上位に伝播させる
  }
}

export const listOrganizations = async () => {
  return invokeLambda('get', {})
}