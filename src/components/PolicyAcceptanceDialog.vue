<template>
  <v-dialog v-model="dialog" persistent max-width="500px">
    <v-card>
      <v-card-title class="text-h5">ポリシーの更新</v-card-title>
      <v-card-text class="py-2">
        <div class="px-2 mb-3">
          <p v-if="needsTosAcceptance && needsPrivacyPolicyAcceptance">
            利用規約とプライバシーポリシーが更新されました。<br>続行するには、両方に同意する必要があります。
          </p>
          <p v-else-if="needsTosAcceptance">
            利用規約が更新されました。<br>続行するには、同意する必要があります。
          </p>
          <p v-else-if="needsPrivacyPolicyAcceptance">
            プライバシーポリシーが更新されました。<br>続行するには、同意する必要があります。
          </p>
        </div>
        <v-checkbox
          v-if="needsTosAcceptance"
          v-model="tosAccepted"
          label="利用規約に同意します"
          :rules="[v => !!v || '利用規約への同意が必要です']"
          hide-details
        >
          <template #label>
            <div>
              <a href="#" @click.prevent="openTermsOfService">利用規約</a>に同意します
            </div>
          </template>
        </v-checkbox>
        <v-checkbox
          v-if="needsPrivacyPolicyAcceptance"
          v-model="privacyPolicyAccepted"
          label="プライバシーポリシーに同意します"
          :rules="[v => !!v || 'プライバシーポリシーへの同意が必要です']"
          hide-details
        >
          <template #label>
            <div>
              <a href="#" @click.prevent="openPrivacyPolicy">プライバシーポリシー</a>に同意します
            </div>
          </template>
        </v-checkbox>
      </v-card-text>
      <v-card-actions class="px-4 pb-4">
        <v-spacer></v-spacer>
        <v-btn
          color="primary"
          :disabled="!canAccept"
          @click="accept"
        >
          同意して続行
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, computed } from 'vue'
import { termsOfServiceUrl, privacyPolicyUrl } from '@/config/environment'

const props = defineProps({
  modelValue: Boolean,
  needsTosAcceptance: Boolean,
  needsPrivacyPolicyAcceptance: Boolean,
})

const emit = defineEmits(['update:modelValue', 'accept'])

const tosAccepted = ref(false)
const privacyPolicyAccepted = ref(false)

const dialog = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const canAccept = computed(() => {
  return (!props.needsTosAcceptance || tosAccepted.value) &&
          (!props.needsPrivacyPolicyAcceptance || privacyPolicyAccepted.value)
})

const openTermsOfService = () => {
  window.open(termsOfServiceUrl, '_blank', 'noopener,noreferrer')
}

const openPrivacyPolicy = () => {
  window.open(privacyPolicyUrl, '_blank', 'noopener,noreferrer')
}

const accept = () => {
  emit('accept')
  tosAccepted.value = false
  privacyPolicyAccepted.value = false
}
</script>