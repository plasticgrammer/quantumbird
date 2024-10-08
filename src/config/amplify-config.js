import { redirectUrl } from './environment'

const config = {
  Auth: {
    Cognito: {
      region: process.env.VUE_APP_AWS_REGION,
      userPoolId: process.env.VUE_APP_USER_POOL_ID,
      userPoolClientId: process.env.VUE_APP_USER_POOL_WEB_CLIENT_ID,
      signUpVerificationMethod: 'code', // 'code' or 'link'
      loginWith: {
        oauth: {
          domain: process.env.VUE_APP_COGNITO_DOMAIN,
          scopes: ['email', 'openid', 'aws.cognito.signin.user.admin'],
          redirectSignIn: [redirectUrl],
          redirectSignOut: [redirectUrl],
          responseType: 'code'
        }
      }
    }
  }
}

export default config