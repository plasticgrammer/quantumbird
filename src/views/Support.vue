<template>
  <v-container>
    <v-card 
      class="mx-auto mt-8 mb-12 border-md d-flex align-center"
      elevation="0"
      variant="flat"
      max-width="600"
      min-height="100"
      color="teal-lighten-5"
    >
      <v-card-text class="text-center text-h6">
        <div v-if="!isLoading">
          <p v-if="organization.members.length == 0">
            最初に組織情報の登録が必要です。<br>
            メニューより［組織情報管理］を選んでください。<br>
          </p>
          <p v-else-if="!organization.requestEnabled">
            報告依頼の自動送信がオフとなっています。<br>
            メニューより［報告依頼設定］を選んでください。<br>
          </p>
          <p v-else>
            メンバーからの報告状況を確認してください。<br>
            メニューより［ダッシュボード］を選んでください。<br>
          </p>
        </div>
        <div v-else>
          <v-progress-circular 
            size="42"
            width="8"
            indeterminate
          ></v-progress-circular>
        </div>
      </v-card-text>
    </v-card>
    <v-img
      src="@/assets/images/rakko.png"
      max-width="360"
      class="mx-auto"
    ></v-img>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useStore } from 'vuex'
import { getOrganization } from '../services/organizationService'

const store = useStore()
const organizationId = store.getters['user/organizationId']

const isLoading = ref(true)
const error = ref(null)
const organization = ref('')

const fetchOrganizationInfo = async () => {
  try {
    const org = await getOrganization(organizationId)
    organization.value = org
  } catch (err) {
    console.error('Failed to fetch organization info:', err)
    error.value = '組織情報の取得に失敗しました'
  }
}

const fetchAll = async () => {
  isLoading.value = true
  try {
    await Promise.all([
      fetchOrganizationInfo()
    ])
    // initChart の呼び出しを削除
  } catch (err) {
    console.error('Error initializing dashboard:', err)
    error.value = '初期化に失敗しました'
  } finally {
    isLoading.value = false
  }
}

onMounted(fetchAll)
</script>
