<template>
  <v-container>
    <v-card class="text-center" elevation="0">
      <v-card-title class="text-h5 font-weight-bold">
      </v-card-title>
      <v-card-text>
        <v-img
          src="@/assets/images/kobiruneko.png"
          max-width="160"
          class="mx-auto my-5"
        ></v-img>
        <div class="text-body-1">
          <p v-if="memberCount == 0">
            最初に組織情報の登録が必要です。<br>
            左側メニューより組織情報管理を選んでください。<br>
          </p>
          <p v-else-if="!organization.requestEnabled">
            報告依頼の自動送信がオフとなっています。<br>
            左側メニューより報告依頼設定を選んでください。<br>
          </p>
          <p v-else>
            メンバーからの報告があるか確認してください。<br>
            左側メニューより週次報告レビューを選んでください。<br>
          </p>
        </div>
      </v-card-text>
    </v-card>
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
const memberCount = ref(0)

const fetchOrganizationInfo = async () => {
  try {
    const org = await getOrganization(organizationId)
    organization.value = org
    memberCount.value = org.members.length
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
