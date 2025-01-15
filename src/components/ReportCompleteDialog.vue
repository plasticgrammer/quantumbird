<template>
  <v-dialog 
    :model-value="modelValue"
    :max-width="isAdviceEnabled ? (advisorState.isAdviceAvailable ? 780 : 600) : 480"
    persistent
    @update:model-value="handleDialogUpdate"
  >
    <v-card class="bg-plain text-center rounded-lg d-flex flex-column">
      <v-card-title class="text-h5 font-weight-bold flex-shrink-0">
        <span v-if="isMobile">報告完了</span>
        <span v-else>週次報告ありがとうございました</span>
      </v-card-title>
      <v-card-subtitle v-if="!isMobile && advisorState.showAddTicetMessage">
        新しい週次報告によりアドバイスチケットが付与されました
      </v-card-subtitle>
 
      <!-- チケット残数表示 -->
      <div v-if="isAdviceEnabled" class="ticket-chip-container">
        <v-chip
          :color="advisorState.remainingTickets ? 'grey-darken-2' : 'grey-lighten-1'"
          class="ticket-chip"
          variant="outlined"
        >
          <template v-if="advisorState.remainingTickets <= 3">
            <v-icon
              v-for="i in 3"
              :key="i"
              :color="i <= advisorState.remainingTickets ? 'indigo' : 'grey-lighten-1'"
              class="ticket-icon"
              size="small" 
            >
              {{ i <= advisorState.remainingTickets ? 'mdi-ticket' : 'mdi-ticket-outline' }}
            </v-icon>
          </template>
          <template v-else>
            <v-icon class="ticket-icon" size="small" color="indigo">mdi-ticket</v-icon>
            <span class="text-caption ml-1">{{ advisorState.remainingTickets }}</span>
          </template>
          <v-tooltip activator="parent" location="bottom">
            アドバイスチケット残数
          </v-tooltip>
        </v-chip>
      </div>
      
      <!-- アドバイス機能が有効な場合 -->
      <v-card-text class="py-1 flex-grow-1 scrollable-content">
        <template v-if="isAdviceEnabled">
          <!-- アドバイス表示 -->
          <div v-if="advisorState.isAdviceAvailable">
            <v-sheet class="text-left pa-4 pt-1 mx-3 rounded-lg advisor-container">
              <v-img
                :src="advisorRoles[advisorState.selectedRole].image"
                max-width="100"
                class="mx-auto mt-0 mb-2"
                :aspect-ratio="1"
              ></v-img>
              <p class="text-caption text-grey-darken-1 mb-2">
                <v-icon 
                  :icon="advisorRoles[advisorState.selectedRole].icon" 
                  :color="advisorRoles[advisorState.selectedRole].color" 
                  class="me-1"
                />
                {{ advisorRoles[advisorState.selectedRole].title }}からのアドバイス
              </p>
              <p class="text-advice text-grey-darken-3">{{ advisorState.advice }}</p>
            </v-sheet>
 
            <!-- 別のアドバイザーに相談するオプション -->
            <div v-if="Object.keys(availableAdvisors).length > 1">
              <div v-if="advisorState.remainingTickets > 0" class="my-4">
                <v-btn
                  variant="outlined"
                  color="grey-darken-2"
                  @click="resetState"
                >
                  <v-icon icon="mdi-swap-horizontal-bold" class="mr-1" />
                  別のアドバイザーに相談する
                </v-btn>
              </div>
              <p v-else class="text-caption my-2">
                アドバイスチケットを使い切りました。新しい週次報告時に再度利用可能になります。
              </p>
            </div>
          </div>
          
          <!-- アドバイザー選択 -->
          <div v-else>
            <v-sheet class="mx-3 py-3 rounded-lg advisor-container">
              <p class="text-body-1">アドバイザーを選んでください</p>
 
              <v-window 
                v-model="advisorState.selectedRole" 
                :show-arrows="Object.keys(availableAdvisors).length > 1"
                continuous
              >
                <v-window-item
                  v-for="(advisor, key) in availableAdvisors"
                  :key="key"
                  :value="key"
                >
                  <v-card class="mx-2 bg-transparent" elevation="0">
                    <div class="advisor-image-container d-flex align-end justify-center">
                      <v-img
                        :src="advisor.image"
                        max-width="160"
                        :class="['advisor-image mb-2 mx-auto', { 'scale-up': advisorState.isButtonHovering || advisorState.isLoading }]"
                        :position="'top'"
                      >
                      </v-img>
                    </div>
                    <v-card-title class="font-weight-bold">
                      <v-icon
                        :icon="advisor.icon"
                        :color="advisor.color"
                        class="mt-n1 me-2"
                      />
                      {{ advisor.title }}
                      <div class="text-button">
                        {{ advisor.description }}
                      </div>
                    </v-card-title>
                  </v-card>
                </v-window-item>
              </v-window>
 
              <div class="d-flex justify-center mb-2">
                <v-btn
                  v-if="advisorState.remainingTickets > 0"
                  class="px-8 border-thin"
                  style="--v-border-color: auto"
                  min-width="50%"
                  height="60px"
                  variant="tonal"
                  color="indigo"
                  :disabled="advisorState.remainingTickets === 0"
                  @mouseenter="handleButtonHover(true)"
                  @mouseleave="handleButtonHover(false)"
                  @click="handleGenerateAdvice"
                >
                  <template v-if="advisorState.isLoading">
                    <v-progress-circular
                      indeterminate size="22" width="4" 
                      :color="advisorRoles[advisorState.selectedRole].color" class="me-2"
                    ></v-progress-circular>
                    アドバイザーに相談中...
                  </template>
                  <template v-else>
                    <div class="d-flex flex-column">
                      <div class="d-flex align-center">
                        <v-icon icon="mdi-comment-text-outline" size="large" class="me-2" />
                        <span>このアドバイザーに相談する</span>
                      </div>
                      <div class="text-caption pt-1">
                        （<v-icon size="small" class="mx-1">mdi-ticket</v-icon>チケットを1枚消費します）
                      </div>
                    </div>
                  </template>
                </v-btn>
                <p v-else class="text-caption text-error my-1">
                  アドバイスチケットを使い切りました。<br>
                  新しい週次報告時に再度利用可能になります。
                </p>
              </div>
            </v-sheet>
          </div>
        </template>
        <!-- アドバイス機能が無効な場合 -->
        <template v-else>
          <v-img
            :src="advisorRoles[advisorState.selectedRole].image"
            max-width="200"
            class="mx-auto mt-0 mb-3"
            :aspect-ratio="1"
          ></v-img>
        </template>
      </v-card-text>
 
      <v-card-actions class="pt-4 pb-4 flex-shrink-0">
        <v-row justify="center" no-gutters>
          <v-col cols="auto" class="mx-2">
            <v-btn color="primary" prepend-icon="mdi-chevron-left" variant="elevated" @click="$emit('back')">
              週次報告に戻る
            </v-btn>
          </v-col>
          <v-col cols="auto" class="mx-2">
            <v-btn color="grey-darken-1" prepend-icon="mdi-close" variant="elevated" @click="$emit('close')">
              終了する
            </v-btn>
          </v-col>
        </v-row>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { reactive, watch, onMounted, onUnmounted, computed } from 'vue'
import { useResponsive } from '@/composables/useResponsive'
import { advisorRoles, getWeeklyReportAdvice } from '@/services/bedrockService'
import { getMember } from '@/services/publicService'

const { isMobile } = useResponsive()

const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true
  },
  reportContent: {
    type: Object,
    default: () => ({})
  },
  isAdviceEnabled: {
    type: Boolean,
    default: false
  },
  enabledAdvisors: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:modelValue', 'back', 'close'])

const advisorState = reactive({
  selectedRole: 'manager',
  isButtonHovering: false,
  isLoading: false,
  isAdviceAvailable: false,
  isNewReport: false,
  advice: '',
  remainingTickets: 0,
  showAddTicetMessage: false
})

const availableAdvisors = computed(() => {
  if (!props.isAdviceEnabled) {
    return { manager: advisorRoles.manager }
  }

  // 組織で有効化されたアドバイザーのみを返す
  if (props.enabledAdvisors?.length > 0) {
    return Object.fromEntries(
      Object.entries(advisorRoles).filter(([key]) => {
        return props.enabledAdvisors.includes(key)
      })
    )
  }
  return { manager: advisorRoles.manager }
})

const resetState = () => {
  Object.assign(advisorState, {
    selectedRole: Object.keys(availableAdvisors.value)[0] || 'manager',
    isButtonHovering: false,
    isLoading: false,
    isAdviceAvailable: false,
    advice: '',
    showAddTicetMessage: false
  })
}

const initializeTickets = async (memberUuid) => {
  if (!memberUuid || !props.isAdviceEnabled) return

  try {
    const member = await getMember(memberUuid)
    advisorState.remainingTickets = member.adviceTickets ?? 0
  } catch (error) {
    console.error('Error fetching member tickets:', error)
    advisorState.remainingTickets = 0
  }
}

const handleDialogUpdate = (value) => {
  emit('update:modelValue', value)
  if (!value) {
    resetState()
  }
}

const handleButtonHover = (hovering) => {
  advisorState.isButtonHovering = hovering
}

const handleGenerateAdvice = async () => {
  if (advisorState.isLoading || advisorState.remainingTickets <= 0) return

  try {
    advisorState.isLoading = true
    const response = await getWeeklyReportAdvice({
      ...props.reportContent,
      advisorRole: advisorState.selectedRole
    })
    
    Object.assign(advisorState, {
      advice: response.advice,
      remainingTickets: response.remainingTickets,
      isAdviceAvailable: true
    })

  } catch (error) {
    console.error('Error getting weekly report advice:', error)
    const hasNoTickets = error.code === 'INSUFFICIENT_TICKETS'
    const errorMessage = hasNoTickets
      ? 'アドバイスチケットが不足しています。新しい週次報告時に再度利用可能になります。'
      : '申し訳ありません。アドバイスの生成中にエラーが発生しました。'
    if (hasNoTickets) advisorState.remainingTickets = 0
    Object.assign(advisorState, {
      advice: errorMessage,
      isAdviceAvailable: true
    })
  } finally {
    advisorState.isLoading = false
  }
}

const advisorKeys = computed(() => Object.keys(availableAdvisors.value))

const handleKeydown = (event) => {
  if (!props.modelValue || advisorState.isAdviceAvailable) return

  const currentIndex = advisorKeys.value.indexOf(advisorState.selectedRole)
  if (event.key === 'ArrowLeft') {
    const prevIndex = currentIndex <= 0 ? advisorKeys.value.length - 1 : currentIndex - 1
    advisorState.selectedRole = advisorKeys.value[prevIndex]
  } else if (event.key === 'ArrowRight') {
    const nextIndex = currentIndex >= advisorKeys.value.length - 1 ? 0 : currentIndex + 1
    advisorState.selectedRole = advisorKeys.value[nextIndex]
  }
}

const preloadAdvisorImages = () => {
  Object.values(availableAdvisors.value).forEach(advisor => {
    const img = new Image()
    img.src = advisor.image
  })
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
  preloadAdvisorImages()
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})

watch(() => props.reportContent,
  async (newValue) => {
    if (newValue?.memberUuid) {
      resetState()
      if (props.isAdviceEnabled) {
        advisorState.showAddTicetMessage = newValue.isNew
        await initializeTickets(newValue.memberUuid)
      }
    }
  },
  { immediate: true }
)
</script>

<style scoped>
.advisor-container {
  border: solid 1px #607d8b;
  background-color: #e3f2fd;
}

.advisor-image-container {
  height: 165px;
  overflow: hidden;
}

.advisor-image {
  width: 100%;
  transition: transform 0.3s ease;
}

.scale-up {
  transform: scale(1.1);
}

.advisor-image :deep(.v-img__img) {
  object-fit: cover !important;
  opacity: 0;
  animation: fadeIn 0.3s ease forwards;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.text-advice {
  font-size: 1em !important;
  white-space: pre-wrap;
  line-height: 1.8;
  letter-spacing: 0.03em;
}

.ticket-chip-container {
  position: absolute;
  top: 12px;
  right: 12px;
  z-index: 1;
}

.ticket-chip {
  border: solid 1px #e0e0e0;
}

.ticket-icon {
  transform: rotate(-35deg);
  margin-left: 2px;
  margin-right: 2px;
}

.v-window {
  border-radius: 8px;
  overflow: hidden;
}

.v-window-item {
  height: 100%;
}

.v-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.v-card-text {
  scrollbar-color: rgba(0, 0, 0, 0.2) transparent;
}

.v-card-text::-webkit-scrollbar-track {
  background: transparent;
}

.v-card-text::-webkit-scrollbar-thumb {
  background-color: rgba(0, 0, 0, 0.2);
  border-radius: 3px;
}

.scrollable-content {
  max-height: 80vh;
  overflow-y: auto;
}
</style>