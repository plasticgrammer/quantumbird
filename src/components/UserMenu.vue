<template>
  <div 
    class="user-menu-wrapper"
    @mouseenter="handleMouseEnter"
    @mouseleave="handleMouseLeave"
  >
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
      @update:model-value="handleDropdownChange"
    >
      <v-list class="pa-0 brightness120" :bg-color="bgColor">
        <v-list-item>
          <v-list-item-title class="text-body-2 py-2 opacity-60">{{ user.email }}</v-list-item-title>
          <v-list-item-title class="text-body-2 py-2 opacity-60">
            <v-icon class="mr-2" size="small">mdi-currency-usd</v-icon>
            {{ currentPlanName }}
            <v-chip
              v-if="isTrialPeriod"
              color="warning"
              size="x-small"
              class="ml-2"
            >
              トライアル中
            </v-chip>
          </v-list-item-title>
        </v-list-item>
        <v-divider></v-divider>
        <v-list-item
          prepend-icon="mdi-cog-outline"
          title="アカウント設定"
          link
          @click="navigateToAccounttSetting"
        >
        </v-list-item>
        <v-list-item
          prepend-icon="mdi-currency-usd"
          title="支払い設定"
          link
          @click="router.push({ name: 'Billing' })"
        >
        </v-list-item>
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
            <v-list class="pa-0 brightness120" :bg-color="bgColor">
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
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { feedbackUrl, termsOfServiceUrl, privacyPolicyUrl } from '@/config/environment'

defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  bgColor: {
    type: String,
    default: '#365D91'
  }
})

const emit = defineEmits(['update:modelValue'])

const store = useStore()
const router = useRouter()
const showDropdown = ref(false)
const showLearnMoreSubmenu = ref(false)

const user = computed(() => ({
  organizationId: store.getters['auth/organizationId'],
  username: store.getters['auth/name'],
  email: store.getters['auth/email']
}))

const currentPlanName = computed(() => store.getters['auth/currentPlanName'])
const isTrialPeriod = computed(() => store.getters['auth/isTrialPeriod'])

const handleMouseEnter = () => {
  emit('update:modelValue', true)
}

const handleMouseLeave = () => {
  if (!showDropdown.value) {
    emit('update:modelValue', false)
  }
}

const handleDropdownChange = (value) => {
  showDropdown.value = value
  if (!value) {
    emit('update:modelValue', false)
  }
}

const navigateToAccounttSetting = () => {
  router.push({ name: 'AccountSetting' })
}

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

<style scoped>
.user-menu-wrapper {
  width: 100%;
}

.v-list-item-title {
  font-size: 0.925rem;
}
</style>