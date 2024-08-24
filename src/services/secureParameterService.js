import { lambda } from './awsConfig'

const stage = process.env.STAGE || 'dev'

const invokeLambda = async (operation, payload) => {
  const params = {
    FunctionName: `${stage}-secure-parameter`,
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

export const generateToken = async (params) => {
  return invokeLambda('generateToken', params)
}

export const verifyToken = async (token) => {
  return invokeLambda('verifyToken', { token })
}