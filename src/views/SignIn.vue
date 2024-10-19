<template>
  <v-container>
    <v-card max-width="500" class="mx-auto mt-6">
      <v-card-title class="mt-1 mb-4">
        <div class="text-center mb-5">
          <h1 class="logo-font">fluxweek</h1>
        </div>
        <v-icon size="large" class="mr-1">mdi-bird</v-icon>
        {{ title }}
      </v-card-title>
      <v-card-text>
        <v-alert
          v-if="successMessage"
          type="success"
          class="resultMessage mb-4"
          dismissible
          @click:close="successMessage = ''"
        >
          {{ successMessage }}
        </v-alert>        
        <v-alert 
          v-if="errorMessage" 
          type="error" 
          class="resultMessage mb-4"
          dismissible
          @click:close="errorMessage = ''"
        >
          {{ errorMessage }}
        </v-alert>

        <!-- サインインフォーム -->
        <v-form v-if="currentView === 'signIn'" @submit.prevent="handleSignIn">
          <v-text-field
            v-model="signInEmail"
            label="メールアドレス"
            required
          />
          <v-text-field
            v-model="signInPassword"
            label="パスワード"
            type="password"
            required
          />
          <v-btn
            color="primary"
            type="submit"
            block
            class="mt-4"
            :loading="loading"
          >
            サインイン
          </v-btn>
        </v-form>

        <!-- サインアップフォーム -->
        <v-form v-else-if="currentView === 'signUp'" ref="signUpForm" @submit.prevent="handleSignUpSubmit">
          <v-text-field
            v-model="signUpEmail"
            label="メールアドレス"
            type="email"
            required
            :rules="[v => !!v || 'メールアドレスは必須です', v => /.+@.+\..+/.test(v) || '有効なメールアドレスを入力してください']"
          />
          <v-text-field
            v-model="signUpPassword"
            label="パスワード"
            type="password"
            required
            :rules="[v => !!v || 'パスワードは必須です', v => v.length >= 8 || 'パスワードは8文字以上である必要があります']"
          />
          <v-text-field
            v-model="organizationId"
            label="組織ID"
            required
            :rules="[v => !!v || '組織IDは必須です', validateOrganizationId]"
            @input="clearErrorMessage"
          />
          <v-text-field
            v-model="organizationName"
            label="組織名"
            required
            :rules="[v => !!v || '組織名は必須です']"
          />
          <v-checkbox
            v-model="agreeToTerms"
            label="利用規約に同意する"
            required
            hide-details
          >
            <template #label>
              <span>
                <a href="#" @click.prevent="openTermsOfService">利用規約</a>に同意する
              </span>
            </template>
          </v-checkbox>
          <v-checkbox
            v-model="agreeToPrivacy"
            label="プライバシーポリシーに同意する"
            required
            hide-details
          >
            <template #label>
              <span>
                <a href="#" @click.prevent="openPrivacyPolicy">プライバシーポリシー</a>に同意する
              </span>
            </template>
          </v-checkbox>
          <v-btn
            color="primary"
            type="submit"
            block
            class="mt-4"
            :loading="loading"
            :disabled="loading || !isAgreedToAll"
          >
            サインアップ
          </v-btn>
        </v-form>

        <!-- 確認コードフォーム -->
        <v-form v-else @submit.prevent="confirmSignUpUser">
          <v-text-field
            v-model="confirmEmail"
            label="メールアドレス"
            required
          />
          <v-text-field
            v-model="confirmCode"
            label="確認コード"
            required
          />
          <v-btn
            color="primary"
            type="submit"
            block
            class="mt-4"
            :loading="loading"
          >
            確認
          </v-btn>
          <v-btn
            text
            color="secondary"
            :disabled="loading"
            class="mt-2"
            @click="resendConfirmationCode"
          >
            確認コードを再送信
          </v-btn>
        </v-form>

        <v-card-actions>
          <v-spacer />
          <v-btn
            text
            color="primary"
            @click="toggleView"
          >
            {{ toggleButtonText }}
          </v-btn>
        </v-card-actions>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { termsOfServiceUrl, privacyPolicyUrl, termsOfServiceVersion, privacyPolicyVersion } from '../config/environment'
import { 
  signIn, 
  signUp, 
  confirmSignUp, 
  resendSignUpCode, 
  signOut, 
  getCurrentUser,
} from '@aws-amplify/auth'
import { getOrganization, submitOrganization } from '../services/publicService'

const router = useRouter()
const store = useStore()

// State
const currentView = ref('signIn')
const signInEmail = ref('')
const signInPassword = ref('')
const signUpEmail = ref('')
const signUpPassword = ref('')
const organizationId = ref('')
const organizationName = ref('')
const confirmEmail = ref('')
const confirmCode = ref('')
const loading = ref(false)
const successMessage = ref('')
const errorMessage = ref('')
const signUpForm = ref(null)
const agreeToTerms = ref(false)
const agreeToPrivacy = ref(false)

// Computed properties
const title = computed(() => {
  const titles = {
    signIn: 'サインイン',
    signUp: 'サインアップ',
    confirm: '確認コードの入力'
  }
  return titles[currentView.value] || ''
})

const toggleButtonText = computed(() => {
  const texts = {
    signIn: 'アカウントを作成',
    signUp: 'サインインに戻る',
    confirm: 'サインインに戻る'
  }
  return texts[currentView.value] || ''
})

const isAgreedToAll = computed(() => agreeToTerms.value && agreeToPrivacy.value)

// Methods
const validateOrganizationId = (value) => {
  if (!value) return '組織IDは必須です'
  const alphanumericRegex = /^[a-zA-Z0-9_-]+$/
  return alphanumericRegex.test(value) || '組織IDは英数字のみで入力してください'
}

const clearErrorMessage = () => {
  errorMessage.value = ''
}

const handleSignIn = async () => {
  loading.value = true
  errorMessage.value = ''
  successMessage.value = ''
  try {
    const currentUser = await getCurrentUser().catch(() => null)
    if (currentUser) {
      await signOut()
      console.info('既存のセッションからサインアウトしました。')
    }
    await signIn({ username: signInEmail.value, password: signInPassword.value })
    await store.dispatch('auth/fetchUser')
    router.push('/admin')
  } catch (error) {
    handleAuthError(error)
  } finally {
    loading.value = false
  }
}

const handleSignUpSubmit = async () => {
  errorMessage.value = ''
  const { valid } = await signUpForm.value.validate()
  
  if (!valid) {
    errorMessage.value = 'すべての必須フィールドを正しく入力してください。'
    return
  }

  if (!validateOrganizationId(organizationId.value)) {
    errorMessage.value = '組織IDは英数字のみで入力してください。'
    return
  }

  const org = await getOrganization(organizationId.value)
  if (org) {
    errorMessage.value = 'この組織IDは既に使用されています。'
    return
  }

  await signUpUser()
}

const signUpUser = async () => {
  loading.value = true
  try {
    const { user } = await signUp({
      username: signUpEmail.value,
      password: signUpPassword.value,
      options: {
        userAttributes: {
          email: signUpEmail.value,
          name: signUpEmail.value,
          'custom:organizationId': organizationId.value,
          'custom:tos_version': termsOfServiceVersion,
          'custom:pp_version': privacyPolicyVersion
        }
      }
    })
    console.log('サインアップ成功:', user)
    confirmEmail.value = signUpEmail.value
    currentView.value = 'confirm'
    successMessage.value = '確認コードを送信しました。メールをご確認ください。'
  } catch (error) {
    console.error('サインアップエラー:', error)
    errorMessage.value = error.message || 'サインアップに失敗しました。入力内容を確認してください。'
  } finally {
    loading.value = false
  }
}

const confirmSignUpUser = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    await confirmSignUp({ username: confirmEmail.value, confirmationCode: confirmCode.value })
    const organization = { 
      organizationId: organizationId.value, 
      name: organizationName.value, 
      sender: confirmEmail.value,
      senderName: organizationName.value 
    }
    await submitOrganization(organization)
    currentView.value = 'signIn'
    successMessage.value = '確認が完了しました。サインインしてください。'
  } catch (error) {
    console.error('確認エラー:', error)
    errorMessage.value = '確認に失敗しました。コードを確認してください。'
  } finally {
    loading.value = false
  }
}

const resendConfirmationCode = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    await resendSignUpCode({ username: confirmEmail.value })
    successMessage.value = '確認コードが再送信されました。メールをご確認ください。'
  } catch (error) {
    console.error('再送信エラー:', error)
    errorMessage.value = '確認コードの再送信に失敗しました。'
  } finally {
    loading.value = false
  }
}

const handleAuthError = (error) => {
  const errorMessages = {
    UserAlreadyAuthenticatedException: '既にサインインしています。一度サインアウトしてから再試行してください。',
    UserNotConfirmedException: 'ユーザーアカウントが確認されていません。確認コードを入力してください。',
    NotAuthorizedException: 'メールアドレスまたはパスワードが正しくありません。',
    UserNotFoundException: 'このメールアドレスに対応するアカウントが見つかりません。'
  }
  errorMessage.value = errorMessages[error.name] || `サインインに失敗しました: ${error.message}`
  if (error.name === 'UserNotConfirmedException') {
    currentView.value = 'confirm'
  }
}

const toggleView = () => {
  currentView.value = currentView.value === 'signIn' ? 'signUp' : 'signIn'
  errorMessage.value = ''
}

const openTermsOfService = () => {
  window.open(termsOfServiceUrl, '_blank', 'noopener,noreferrer')
}

const openPrivacyPolicy = () => {
  window.open(privacyPolicyUrl, '_blank', 'noopener,noreferrer')
}
</script>

<style>
.resultMessage {
  white-space: pre-line;
}
</style>