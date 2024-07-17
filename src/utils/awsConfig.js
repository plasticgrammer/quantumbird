import AWS from 'aws-sdk';

AWS.config.update({
  region: process.env.VUE_APP_AWS_REGION,
  accessKeyId: process.env.VUE_APP_AWS_ACCESS_KEY_ID,
  secretAccessKey: process.env.VUE_APP_AWS_SECRET_ACCESS_KEY
});

export const dynamoDB = new AWS.DynamoDB.DocumentClient();

export const lambda = new AWS.Lambda();