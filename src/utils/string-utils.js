export const isValidEmail = (email) => {
  // RFC 5322に基づくメールアドレス検証の正規表現
  const re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
  return re.test(email)
}

/**
 * メールの送信者名のバリデーション結果
 * @typedef {Object} SenderNameValidationResult
 * @property {boolean} isValid - 有効な場合はtrue
 * @property {string} message - エラーメッセージ（有効な場合は空文字列）
 */

/**
 * MIME encoded-word形式でエンコードした場合の長さを計算
 * @param {string} text - 対象文字列
 * @returns {number} エンコード後の長さ
 */
function getMimeEncodedLength(text) {
  // UTF-8でバイト配列に変換
  const utf8Bytes = new TextEncoder().encode(text)
  // Base64エンコード後の長さを計算（4文字毎に3バイトをエンコード）
  const base64Length = Math.ceil(utf8Bytes.length / 3) * 4
  // MIME encoded-word形式の全体の長さを計算
  // =?UTF-8?B?{encoded-text}?=
  return 10 + base64Length
}

// メール送信で問題が発生しやすい文字のパターン
const PROBLEMATIC_CHARS = {
  // 丸付き文字、組文字
  circled: /[㈱㈲㈳㈴㈵㈶㈷㈸㈹㈺㈻㈼㈽㈾㈿]/,
  // ローマ数字
  romanNumerals: /[ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩⅪⅫⅰⅱⅲⅳⅴⅵⅶⅷⅸⅹⅺⅻ]/,
  // 囲み文字（丸、角）
  enclosed: /[①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳❶❷❸❹❺❻❼❽❾❿⓫⓬⓭⓮⓯⓰⓱⓲⓳⓴]/,
  // 機種依存文字（一部）
  deviceDependent: /[℡№℃℉]/
}

/**
 * メールの送信者名として有効かチェックする
 * @param {string} name - チェックする送信者名
 * @returns {SenderNameValidationResult} バリデーション結果
 */
export function validateSenderName(name) {
  if (typeof name !== 'string') {
    return { isValid: false, message: '送信者名は文字列で入力してください' }
  }

  // 制御文字をチェック
  for (let i = 0; i < name.length; i++) {
    const code = name.charCodeAt(i)
    if (code < 32 || code === 127) {
      return { isValid: false, message: '送信者名に制御文字は使用できません' }
    }
  }

  // 問題が発生しやすい文字をチェック
  for (const [, pattern] of Object.entries(PROBLEMATIC_CHARS)) {
    if (pattern.test(name)) {
      const examples = name.match(pattern).join(' ')
      return {
        isValid: false,
        message: `送信者名に使用できない文字が含まれています（${examples}）。これらの文字はメール送信時に問題が発生する可能性があります。`
      }
    }
  }

  // エスケープされていない特殊文字をチェック
  const unescapedSpecialChars = /(?<!\\)[()[\]<>;:,\\]/
  if (unescapedSpecialChars.test(name)) {
    return { isValid: false, message: '送信者名に使用できない特殊文字が含まれています（()[]<>;:,\\）' }
  }

  // エスケープされていない二重引用符をチェック
  const unescapedQuotes = /(?<!\\)"/
  if (unescapedQuotes.test(name)) {
    return { isValid: false, message: '送信者名にエスケープされていない二重引用符（"）は使用できません' }
  }

  // MIME encoded-word形式でエンコードした場合の長さをチェック
  const encodedLength = getMimeEncodedLength(name)
  if (encodedLength > 75) { // RFC 2047では75文字以内を推奨
    return { isValid: false, message: '送信者名が長すぎます（エンコード後約30文字以内）' }
  }

  return { isValid: true, message: '' }
}

// 下位互換性のために維持
export function isValidSenderName(name) {
  return validateSenderName(name).isValid
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
