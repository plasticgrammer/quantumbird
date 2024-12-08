export const isValidEmail = (email) => {
  // RFC 5322に基づくメールアドレス検証の正規表現
  const re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
  return re.test(email)
}

export const isValidOrganizationId = (value) => {
  if (!value) return false
  if (value.length < 3 || value.length > 20) return false
  return /^[a-zA-Z0-9_-]+$/.test(value)
}

export const validateOrganizationId = (value) => {
  if (!value) return '組織IDは必須です'
  if (value.length < 3) return '組織IDは3文字以上で入力してください'
  if (value.length > 20) return '組織IDは20文字以下で入力してください'
  return /^[a-zA-Z0-9_-]+$/.test(value) || '組織IDは英数字、ハイフン、アンダースコアのみで入力してください'
}
