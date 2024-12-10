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
export const contextPath = isProd ? '/quantumbird/' : '/'
export const feedbackUrl = 'https://forms.gle/suRGEcRXE33xvFu19'
export const termsOfServiceUrl = `${rootUrl}/legal/terms-of-service.html`
export const termsOfServiceVersion = '1.02'
export const privacyPolicyUrl = `${rootUrl}/legal/privacy-policy.html`
export const privacyPolicyVersion = '1.02'
export const specifiedCommercialTransactionsUrl = `${rootUrl}/legal/specified-commercial-transactions.html`

const config = {
  isProd,
  redirectUrl,
  rootUrl,
  feedbackUrl
}

export default config