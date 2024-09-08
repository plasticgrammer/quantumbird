const isProd = process.env.NODE_ENV === 'production'

function getRedirectUrl() {
  if (!isProd) {
    // 開発環境では環境変数からポート番号を取得
    const port = process.env.VUE_APP_PORT || process.env.PORT || 8080
    return `http://localhost:${port}/`
  }
  // 本番環境では現在のホストを使用
  return `${window.location.protocol}//${window.location.host}/`
}

const redirectUrl = getRedirectUrl()

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