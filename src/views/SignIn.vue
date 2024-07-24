<template>
  <v-container>
    <v-card 
      max-width="400" 
      class="mx-auto mt-5"
      elevation="4"
    >
      <v-card-title>{{ getTitle }}</v-card-title>
      <v-card-text>
        <v-alert
          v-if="successMessage"
          type="success"
          class="resultMessage mb-4"
          dismissible
        >
          {{ successMessage }}
        </v-alert>        
        <v-alert 
          v-if="errorMessage" 
          type="error" 
          class="resultMessage mb-4"
          dismissible
        >
          {{ errorMessage }}
        </v-alert>
        <template v-if="isSignIn">
          <v-form @submit.prevent="handleSignIn" v-if="currentView === 'signIn'">
            <v-text-field
              v-model="signInEmail"
              label="メールアドレス"
              required
            ></v-text-field>
            <v-text-field
              v-model="signInPassword"
              label="パスワード"
              type="password"
              required
            ></v-text-field>
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

          <v-divider class="my-4"></v-divider>
          
          <v-btn
            color="red"
            dark
            block
            class="mb-2 d-none"
            @click="signInWithGoogle"
            :loading="loading"
          >
            <v-icon left>mdi-google</v-icon>
            Googleでサインイン
          </v-btn>
        </template>

        <template v-else-if="isSignUp">
          <v-form @submit.prevent="signUpUser">
            <v-text-field
              v-model="signUpEmail"
              label="メールアドレス"
              type="email"
              required
            ></v-text-field>
            <v-text-field
              v-model="signUpPassword"
              label="パスワード"
              type="password"
              required
            ></v-text-field>
            <v-text-field
              v-model="organizationId"
              label="組織ID"
              required
            ></v-text-field>
            <v-text-field
              v-model="signUpName"
              label="名前"
              required
            ></v-text-field>
            <v-btn
              color="success"
              type="submit"
              block
              class="mt-4"
              :loading="loading"
            >
              サインアップ
            </v-btn>
          </v-form>
        </template>

        <template v-else>
          <v-form @submit.prevent="confirmSignUpUser">
            <v-text-field
              v-model="confirmEmail"
              label="メールアドレス"
              required
            ></v-text-field>
            <v-text-field
              v-model="confirmCode"
              label="確認コード"
              required
            ></v-text-field>
            <v-btn
              color="primary"
              type="submit"
              block
              class="mt-4"
              :loading="loading"
            >
              確認
            </v-btn>
          </v-form>
          <v-btn
            text
            color="secondary"
            @click="resendConfirmationCode"
            :disabled="loading"
            class="mt-2"
          >
            確認コードを再送信
          </v-btn>
        </template>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            text
            color="primary"
            @click="toggleView"
          >
            {{ getToggleButtonText }}
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
import { 
  signIn, 
  signUp, 
  confirmSignUp, 
  resendSignUpCode, 
  signInWithRedirect, 
  signOut, 
  getCurrentUser,
} from '@aws-amplify/auth'

const router = useRouter()
const store = useStore()

// State
const currentView = ref('signIn')
const signInEmail = ref('')
const signInPassword = ref('')
const signUpName = ref('')
const signUpEmail = ref('')
const signUpPassword = ref('')
const organizationId = ref('')
const confirmEmail = ref('')
const confirmCode = ref('')
const loading = ref(false)
const successMessage = ref('')
const errorMessage = ref('')

// Computed properties
const isSignIn = computed(() => currentView.value === 'signIn')
const isSignUp = computed(() => currentView.value === 'signUp')
const getTitle = computed(() => {
  switch (currentView.value) {
  case 'signIn': return 'サインイン'
  case 'signUp': return 'サインアップ'
  case 'confirm': return '確認コードの入力'
  default: return ''
  }
})
const getToggleButtonText = computed(() => {
  switch (currentView.value) {
  case 'signIn': return 'アカウントを作成'
  case 'signUp': return 'サインインに戻る'
  case 'confirm': return 'サインインに戻る'
  default: return ''
  }
})

// Methods
const handleSignIn = async () => {
  loading.value = true
  errorMessage.value = ''
  successMessage.value = ''
  try {
    const currentUser = await getCurrentUser().catch(() => null)
    if (currentUser) {
      await signOut()
      successMessage.value = '既存のセッションからサインアウトしました。再度サインインしてください。'
    } else {
      await signInUser()
    }
  } catch (error) {
    handleSignInError(error)
  } finally {
    loading.value = false
  }
}

const signInUser = async () => {
  try {
    const user = await signIn({ username: signInEmail.value, password: signInPassword.value })
    console.log('サインイン成功:', user)
    await checkAuthState()
    router.push('/admin')
  } catch (error) {
    console.error('サインインエラー:', error)
    errorMessage.value = 'サインインに失敗しました: ' + error.message
  }
}

const checkAuthState = async () => {
  try {
    const user = await getCurrentUser()
    console.log('認証済みユーザー:', user)
    await store.dispatch('user/fetchUser')
    console.log('User state after fetchUser:', store.state.user)
  } catch (error) {
    console.error('認証状態の確認に失敗:', error)
    throw new Error('認証に失敗しました。再度サインインしてください。')
  }
}

const handleSignInError = (error) => {
  if (error.name === 'UserAlreadyAuthenticatedException') {
    errorMessage.value = '既にサインインしています。一度サインアウトしてから再試行してください。'
  } else if (error.name === 'UserNotConfirmedException') {
    errorMessage.value = 'ユーザーアカウントが確認されていません。確認コードを入力してください。'
    currentView.value = 'confirm'
  } else if (error.name === 'NotAuthorizedException') {
    errorMessage.value = 'メールアドレスまたはパスワードが正しくありません。'
  } else if (error.name === 'UserNotFoundException') {
    errorMessage.value = 'このメールアドレスに対応するアカウントが見つかりません。'
  } else {
    errorMessage.value = 'サインインに失敗しました: \n' + error.message
  }
}

const signInWithGoogle = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    await signInWithRedirect({ provider: 'Google' })
  } catch (error) {
    console.error('Googleサインインエラー:', error)
    errorMessage.value = 'Googleサインインに失敗しました。再度お試しください。'
  } finally {
    loading.value = false
  }
}

const signUpUser = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const { user } = await signUp({
      username: signUpEmail.value,
      password: signUpPassword.value,
      options: {
        userAttributes: {
          email: signUpEmail.value,
          name: signUpName.value,
          'custom:organizationId': organizationId.value
        }
      }
    })
    console.log('サインアップ成功:', user)
    confirmEmail.value = signUpEmail.value
    currentView.value = 'confirm'
  } catch (error) {
    console.error('サインアップエラー:', error)
    errorMessage.value = 'サインアップに失敗しました。入力内容を確認してください。'
  } finally {
    loading.value = false
  }
}

const confirmSignUpUser = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    await confirmSignUp({ username: confirmEmail.value, confirmationCode: confirmCode.value })
    console.log('確認成功')
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
    console.log('確認コードが再送信されました')
    successMessage.value = '確認コードが再送信されました。メールをご確認ください。'
  } catch (error) {
    console.error('再送信エラー:', error)
    errorMessage.value = '確認コードの再送信に失敗しました。'
  } finally {
    loading.value = false
  }
}

const toggleView = () => {
  currentView.value = currentView.value === 'signIn' ? 'signUp' : 'signIn'
  errorMessage.value = ''
}
</script>

<style>
.resultMessage {
  white-space: pre-line;
}
</style>