import { lambda } from './awsConfig'

const invokeLambda = async (operation, payload) => {
  const params = {
    FunctionName: 'Organization',
    Payload: JSON.stringify({ operation, payload })
  }

  try {
    const response = await lambda.invoke(params).promise();
    console.log('Raw Lambda response:', response);
    
    if (response.StatusCode !== 200) {
      throw new Error(`Lambda returned status code ${response.StatusCode}`);
    }
    
    let result;
    try {
      // Payloadをパース
      result = JSON.parse(response.Payload);
      console.log('Parsed Lambda Payload:', result);

      // bodyプロパティが存在し、文字列の場合は再度パース
      if (result.body && typeof result.body === 'string') {
        result.body = JSON.parse(result.body);
        console.log('Parsed body:', result.body);
      }

      // 最終的な結果はbodyプロパティ内に存在
      result = result.body;

      // もし結果がまだ文字列なら、さらにパースを試みる
      if (typeof result === 'string') {
        result = JSON.parse(result);
        console.log('Final parsed result:', result);
      }
    } catch (parseError) {
      console.error('Error parsing Lambda response:', parseError);
      throw new Error('Invalid response format from Lambda');
    }

    if (result.error) {
      throw new Error(result.error);
    }
    
    return result;
  } catch (error) {
    console.error(`Error in Lambda operation ${operation}:`, error);
    throw error;
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