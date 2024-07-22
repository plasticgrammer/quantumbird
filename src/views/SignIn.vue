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
            class="mb-2"
            @click="signInWithGoogle"
            :loading="loading"
          >
            <v-icon left>mdi-google</v-icon>
            Googleでサインイン
          </v-btn>
        </template>

        <template v-else-if="isSignUp">
          <v-form @submit.prevent="signUp">
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
          <v-form @submit.prevent="confirmSignUp">
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

<script>
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

export default {
  data() {
    return {
      currentView: 'signIn', // 'signIn', 'signUp', 'confirm'
      signInEmail: '',
      signInPassword: '',
      signUpName: '',
      signUpEmail: '',
      signUpPassword: '',
      organizationId: '',
      confirmEmail: '',
      confirmCode: '',
      loading: false,
      successMessage: '',
      errorMessage: '',
    }
  },
  computed: {
    isSignIn() {
      return this.currentView === 'signIn'
    },
    isSignUp() {
      return this.currentView === 'signUp'
    },
    getTitle() {
      switch (this.currentView) {
      case 'signIn': return 'サインイン'
      case 'signUp': return 'サインアップ'
      case 'confirm': return '確認コードの入力'
      default: return ''
      }
    },
    getToggleButtonText() {
      switch (this.currentView) {
      case 'signIn': return 'アカウントを作成'
      case 'signUp': return 'サインインに戻る'
      case 'confirm': return 'サインインに戻る'
      default: return ''
      }
    },
  },
  methods: {
    async handleSignIn() {
      this.loading = true
      this.errorMessage = ''
      this.successMessage = ''
      try {
        // 現在の認証状態をチェック
        const currentUser = await getCurrentUser()
          .catch(() => null)
        if (currentUser) {
          // 既存のセッションがある場合、サインアウトしてから再度サインイン
          await signOut()
          this.successMessage = '既存のセッションからサインアウトしました。再度サインインしてください。'
        } else {
          // 新規サインイン
          await this.signIn()
        }
      } catch (error) {
        if (error.name === 'UserAlreadyAuthenticatedException') {
          this.errorMessage = '既にサインインしています。一度サインアウトしてから再試行してください。'
        } else if (error.name === 'UserNotConfirmedException') {
          this.errorMessage = 'ユーザーアカウントが確認されていません。確認コードを入力してください。'
          this.currentView = 'confirm'
        } else if (error.name === 'NotAuthorizedException') {
          this.errorMessage = 'メールアドレスまたはパスワードが正しくありません。'
        } else if (error.name === 'UserNotFoundException') {
          this.errorMessage = 'このメールアドレスに対応するアカウントが見つかりません。'
        } else {
          this.errorMessage = 'サインインに失敗しました: \n' + error.message
        }
      } finally {
        this.loading = false
      }
    },
    async signIn() {
      this.loading = true
      this.errorMessage = ''
      const user = await signIn({ username: this.signInEmail, password: this.signInPassword })
      try {
        console.log('サインイン成功:', user)
        
        // サインイン成功後、認証状態を確認
        await this.checkAuthState()

        this.$router.push('/admin')
      } finally {
        this.loading = false
      }
    },
    async checkAuthState() {
      try {
        const user = await getCurrentUser()
        console.log('認証済みユーザー:', user)
        // ここで必要な処理を行う（例：ユーザー情報の保存など）
        const store = useStore()
        await store.dispatch('user/fetchUser')
      } catch (error) {
        console.error('認証状態の確認に失敗:', error)
        throw new Error('認証に失敗しました。再度サインインしてください。')
      }
    },
    async signInWithGoogle() {
      this.loading = true
      this.errorMessage = ''
      try {
        await signInWithRedirect({ provider: 'Google' })
        // リダイレクト後の処理はここでは行われません
      } catch (error) {
        console.error('Googleサインインエラー:', error)
        this.errorMessage = 'Googleサインインに失敗しました。再度お試しください。'
        this.loading = false
      }
    },
    async signUp() {
      this.loading = true
      this.errorMessage = ''
      try {
        const { user } = await signUp({
          username: this.signUpEmail,
          password: this.signUpPassword,
          options: {
            userAttributes: {
              email: this.signUpEmail,
              name: this.signUpName,
              'custom:organizationId': this.organizationId
            }
          }
        })
        console.log('サインアップ成功:', user)
        this.confirmEmail = this.signUpEmail
        this.currentView = 'confirm'
      } catch (error) {
        console.error('サインアップエラー:', error)
        this.errorMessage = 'サインアップに失敗しました。入力内容を確認してください。'
      } finally {
        this.loading = false
      }
    },
    async confirmSignUp() {
      this.loading = true
      this.errorMessage = ''
      try {
        await confirmSignUp({ username: this.confirmEmail, confirmationCode: this.confirmCode })
        console.log('確認成功')
        this.currentView = 'signIn'
        this.successMessage = '確認が完了しました。サインインしてください。'
      } catch (error) {
        console.error('確認エラー:', error)
        this.errorMessage = '確認に失敗しました。コードを確認してください。'
      } finally {
        this.loading = false
      }
    },
    async resendConfirmationCode() {
      this.loading = true
      this.errorMessage = ''
      try {
        await resendSignUpCode({ username: this.confirmEmail })
        console.log('確認コードが再送信されました')
        this.successMessage = '確認コードが再送信されました。メールをご確認ください。'
      } catch (error) {
        console.error('再送信エラー:', error)
        this.errorMessage = '確認コードの再送信に失敗しました。'
      } finally {
        this.loading = false
      }
    },
    toggleView() {
      if (this.currentView === 'signIn') {
        this.currentView = 'signUp'
      } else {
        this.currentView = 'signIn'
      }
      this.errorMessage = ''
    },
  },
}
</script>

<style>
.resultMessage {
  white-space: pre-line;
}
</style>