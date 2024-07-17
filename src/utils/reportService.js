import { lambda } from './awsConfig';

export const submitReport = async (report) => {
  const params = {
    FunctionName: 'WeeklyReport',
    Payload: JSON.stringify(report)
  };

  try {
    const response = await lambda.invoke(params).promise();
    return JSON.parse(response.Payload);
  } catch (error) {
    console.error('Error submitting report:', error);
    throw error;
  }
};