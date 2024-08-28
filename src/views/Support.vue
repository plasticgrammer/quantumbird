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
      <v-card-text class="text-center">
        <div v-if="!isLoading">
          <p v-if="organization.members.length == 0">
            最初に組織情報の登録が必要です。<br>
            <v-btn
              color="black"
              variant="outlined"
              :to="{ name: 'OrganizationManagement' }"
              class="mt-3"
            >
              <v-icon class="mr-1" small>
                mdi-domain
              </v-icon>
              組織情報管理
            </v-btn>
          </p>
          <p v-else-if="!organization.requestEnabled">
            報告依頼の自動送信がオフとなっています。<br>
            <v-btn
              color="black"
              variant="outlined"
              :to="{ name: 'RequestSetting' }"
              class="mt-3"
            >
              <v-icon class="mr-1" small>
                mdi-mail
              </v-icon>
              報告依頼設定
            </v-btn>
          </p>
          <p v-else>
            メンバーからの報告状況を確認してください。<br>
            <v-btn
              color="black"
              variant="outlined"
              :to="{ name: 'Dashboard' }"
              class="mt-3"
            >
              <v-icon class="mr-1" small>
                mdi-mail
              </v-icon>
              ダッシュボード
            </v-btn>
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
const organizationId = store.getters['auth/organizationId']

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
