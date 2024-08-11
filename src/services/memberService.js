import { lambda } from './awsConfig'

const stage = process.env.STAGE || 'dev'

const invokeLambda = async (operation, payload) => {
  const params = {
    FunctionName: `${stage}-member`,
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

export const getMember = async (memberUuid) => {
  return invokeLambda('get', { memberUuid })
}

export const updateMember = async (member) => {
  return invokeLambda('update', { member })
}

export const getMemberProjects = async (memberUuid) => {
  try {
    const result = await invokeLambda('get', { memberUuid, projects: true })
    return result || []
  } catch (error) {
    console.error('Error fetching member projects:', error)
    throw error
  }
}

export const updateMemberProjects = async (memberUuid, projects) => {
  try {
    await invokeLambda('update', { memberUuid, projects })
    return true
  } catch (error) {
    console.error('Error updating member projects:', error)
    throw error
  }
}

export const listMembers = async (organizationId) => {
  return invokeLambda('get', { organizationId, members: true })
}