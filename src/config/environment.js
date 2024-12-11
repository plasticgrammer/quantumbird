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

function getRootUrl() {
  const { protocol, host } = window.location
  return `${protocol}//${host}`
}

export const redirectUrl = getRedirectUrl()
export const rootUrl = getRootUrl()
export const contextPath = '/'
export const feedbackUrl = 'https://forms.gle/suRGEcRXE33xvFu19'

// 静的ファイルのベースURLを環境に応じて設定
const staticBaseUrl = isProd ? process.env.VUE_APP_STATIC_URL || '' : rootUrl

export const termsOfServiceUrl = `${staticBaseUrl}/legal/terms-of-service.html`
export const termsOfServiceVersion = '1.02'
export const privacyPolicyUrl = `${staticBaseUrl}/legal/privacy-policy.html`
export const privacyPolicyVersion = '1.02'
export const specifiedCommercialTransactionsUrl = `${staticBaseUrl}/legal/specified-commercial-transactions.html`

const config = {
  isProd,
  redirectUrl,
  rootUrl,
  feedbackUrl
}

export default config