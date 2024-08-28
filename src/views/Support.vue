<template>
  <div class="wave"></div>
  <div class="wave"></div>
  <div class="wave"></div>
  <div class="wave"></div>
  <v-container class="content-container">
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
      class="on-wave mx-auto"
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

<style>
body,
html {
  margin: 0;
  padding: 0;
  height: 100%;
  overflow-x: hidden;
}

.content-container {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
  z-index: 1;
}

.on-wave {
  position: absolute;
  bottom: 10px;
  left: 50%;
  transform: translateX(-50%);
  max-width: 340px;
  width: 100%;
}

.wave {
  position: absolute;
  bottom: 50px;
  left: 0;
  width: 200%;
  height: 150px;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 88.7"><path d="M800 56.9c-155.5 0-204.9-50-405.5-49.9-200 0-250 49.9-394.5 49.9v31.8h800v-.2-31.6z" fill="%2399BFFF"/></svg>');
  animation: wave 21s linear infinite;
  transform: translate3d(0, 0, 0);
  opacity: 0.9;
  z-index: 2;
}

.wave:nth-of-type(2) {
  bottom: 50px;
  animation: wave 14s linear reverse infinite;
  opacity: 0.7;
}

.wave:nth-of-type(3) {
  bottom: 65px;
  animation: wave 42s linear infinite;
  opacity: 0.5;
}

.wave:nth-of-type(4) {
  bottom: 0px;
  background: #99bfff;
  height: 50px;
  opacity: 1;
}

@keyframes wave {
  0% {
    transform: translateX(0);
  }
  50% {
    transform: translateX(-25%);
  }
  100% {
    transform: translateX(-50%);
  }
}
</style>