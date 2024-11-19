<template>
  <v-footer app class="d-flex py-1 px-4 bg-blue-grey d-print-none footer-fixed justify-end">
    <div class="d-flex">
      <div class="d-flex align-center flex-grow-1">
        <v-btn
          v-for="(link, index) in links"
          :key="index"
          :href="link.url"
          target="_blank"
          rel="noopener noreferrer"
          variant="text"
          density="compact"
          class="text-body-2 mx-1"
        >
          {{ link.text }}
        </v-btn>
      </div>
      <div class="text-caption d-flex align-center ml-8">
        © {{ new Date().getFullYear() }} Fluxweek
      </div>
    </div>
  </v-footer>
</template>

<script setup>
import { termsOfServiceUrl, privacyPolicyUrl, specifiedCommercialTransactionsUrl } from '@/config/environment'

const links = [
  { text: '利用規約', url: termsOfServiceUrl },
  { text: 'プライバシーポリシー', url: privacyPolicyUrl },
  { text: '特定商取引法に基づく表記', url: specifiedCommercialTransactionsUrl }
]
</script>

<style scoped>
.footer-fixed {
  height: 42px;
}
</style>