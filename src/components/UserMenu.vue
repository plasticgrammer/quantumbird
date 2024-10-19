<template>
  <v-list nav>
    <v-list-item
      :title="user.email"
      :subtitle="user.organizationId"
      class="dense-list-item cursor-pointer"
      prepend-icon="mdi-account-circle"
    >
      <template #append>
        <div class="mr-n2">
          <v-icon :icon="showDropdown ? 'mdi-chevron-up' : 'mdi-chevron-down'" color="grey-lighten-1"></v-icon>
        </div>
      </template>
    </v-list-item>
  </v-list>
  <v-menu
    v-model="showDropdown"
    activator="parent"
    location="top"
  >
    <v-list class="pa-0 bg-blue-grey-darken-1">
      <v-list-item>
        <v-list-item-title class="text-body-2 opacity-60">{{ user.email }}</v-list-item-title>
      </v-list-item>
      <v-divider></v-divider>
      <v-list-item
        prepend-icon="mdi-information-outline"
        title="その他"
      >
        <template #append>
          <v-icon icon="mdi-chevron-right"></v-icon>
        </template>
        <v-menu
          v-model="showLearnMoreSubmenu"
          activator="parent"
          location="right"
        >
          <v-list class="pa-0 bg-blue-grey-darken-1">
            <v-list-item
              prepend-icon="mdi-comment-quote-outline"
              title="フィードバック"
              link
              @click="openFeedbackForm"
            >
            </v-list-item>
            <v-list-item
              prepend-icon="mdi-file-document-outline"
              title="利用規約"
              @click="openTermsOfService"
            >
            </v-list-item>
            <v-list-item
              prepend-icon="mdi-shield-account-outline"
              title="プライバシーポリシー"
              @click="openPrivacyPolicy"
            >
            </v-list-item>
          </v-list>
        </v-menu>
      </v-list-item>
      <v-list-item
        prepend-icon="mdi-logout-variant"
        title="サインアウト"
        @click="handleSignOut"
      >
      </v-list-item>
    </v-list>
  </v-menu>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { feedbackUrl, termsOfServiceUrl, privacyPolicyUrl } from '@/config/environment'

const store = useStore()
const router = useRouter()

const showDropdown = ref(false)
const showLearnMoreSubmenu = ref(false)

const user = computed(() => ({
  organizationId: store.getters['auth/organizationId'],
  username: store.getters['auth/name'],
  email: store.getters['auth/email']
}))

const openFeedbackForm = () => {
  window.open(feedbackUrl, '_blank', 'noopener,noreferrer')
}

const openTermsOfService = () => {
  window.open(termsOfServiceUrl, '_blank', 'noopener,noreferrer')
}

const openPrivacyPolicy = () => {
  window.open(privacyPolicyUrl, '_blank', 'noopener,noreferrer')
}

const handleSignOut = async () => {
  try {
    await store.dispatch('auth/signOut')
    router.push({ name: 'SignIn' })
  } catch (error) {
    console.error('サインアウトに失敗しました', error)
  }
}
</script>

<style>
.v-list-item-title {
  font-size: 0.925rem;
}
</style>