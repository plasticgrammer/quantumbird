<template>
  <v-dialog v-model="dialog" fullscreen>
    <v-card>
      <v-toolbar color="menu">
        <v-btn icon @click="closeDialog">
          <v-icon>mdi-close</v-icon>
        </v-btn>
        <v-toolbar-title>メニュー</v-toolbar-title>
      </v-toolbar>

      <v-list>
        <v-list-item>
          <v-list-item-title class="text-body-2 py-2">
            <div>{{ user.email }}</div>
            <v-btn
              prepend-icon="mdi-wallet-membership"
              variant="plain"
              @click="handleBillingClick"
            >
              {{ currentPlan.name }}
            </v-btn>
          </v-list-item-title>
        </v-list-item>

        <v-divider></v-divider>

        <v-list-item
          prepend-icon="mdi-cog-outline"
          title="アカウント設定"
          link
          @click="navigateToAccountSetting"
        >
        </v-list-item>
        <v-divider></v-divider>
        <v-list-item
          v-for="item in helpMenuItems"
          :key="item.title"
          v-bind="item"
          link
          @click="item.onClick"
        >
        </v-list-item>
        <v-divider></v-divider>
        <v-list-item
          prepend-icon="mdi-logout-variant"
          title="サインアウト"
          @click="handleSignOut"
        >
        </v-list-item>
      </v-list>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { computed, inject } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { feedbackUrl, termsOfServiceUrl, privacyPolicyUrl, specifiedCommercialTransactionsUrl } from '@/config/environment'
import { getCurrentPlan } from '@/config/plans'

const props = defineProps({
  modelValue: Boolean
})

const showNotification = inject('showNotification')
const emit = defineEmits(['update:modelValue', 'sign-out'])

const store = useStore()
const router = useRouter()

const dialog = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const user = computed(() => ({
  email: store.getters['auth/email']
}))

const currentPlan = computed(() => getCurrentPlan())
const isParentAccount = computed(() => store.getters['auth/isParentAccount'])

const closeDialog = () => {
  dialog.value = false
}

const handleSignOut = () => {
  closeDialog()
  emit('sign-out')
}

const navigateToAccountSetting = () => {
  closeDialog()
  router.push({ name: 'AccountSetting' })
}

const helpMenuItems = computed(() => ([
  {
    prependIcon: 'mdi-comment-quote-outline',
    title: 'フィードバック',
    onClick: () => window.open(feedbackUrl, '_blank', 'noopener,noreferrer')
  },
  {
    prependIcon: 'mdi-file-document-outline',
    title: '利用規約',
    onClick: () => window.open(termsOfServiceUrl, '_blank', 'noopener,noreferrer')
  },
  {
    prependIcon: 'mdi-shield-account-outline',
    title: 'プライバシーポリシー',
    onClick: () => window.open(privacyPolicyUrl, '_blank', 'noopener,noreferrer')
  },
  {
    prependIcon: 'mdi-shopping-outline',
    title: '特定商取引法に基づく表記',
    onClick: () => window.open(specifiedCommercialTransactionsUrl, '_blank', 'noopener,noreferrer')
  }
]))

const handleBillingClick = () => {
  if (isParentAccount.value) {
    closeDialog()
    router.push({ name: 'Billing' })
  } else {
    showNotification('支払い設定は親アカウントでのみ変更可能です。', 'warning')
  }
}
</script>