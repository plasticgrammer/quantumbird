<template>
  <v-dialog 
    :model-value="modelValue"
    :max-width=" isAdviceEnabled ? 700 : 480 "
    persistent
    @update:model-value="handleDialogUpdate"
  >
    <v-card class="bg-plain text-center rounded-lg d-flex flex-column">
      <v-card-title class="text-h5 font-weight-bold flex-shrink-0">
        <span v-if="isMobile">報告完了</span>
        <span v-else>週次報告ありがとうございました</span>
      </v-card-title>

      <v-card-text class="py-1 flex-grow-1" style="max-height: 80vh; overflow-y: auto;">
        <!-- アドバイス機能が有効な場合 -->
        <template v-if="isAdviceEnabled">
          <div v-if="isAdviceAvailable">
            <v-sheet class="text-left pa-4 pt-1 mx-3 rounded-lg advisor-container">
              <v-img
                :src="advisorRoles[selectedAdvisorRole].image"
                max-width="160"
                class="mx-auto mt-0 mb-3"
                :aspect-ratio="1"
              ></v-img>
              <p class="text-caption text-grey-darken-1 mb-2">
                <v-icon 
                  :icon="advisorRoles[selectedAdvisorRole].icon" 
                  :color="advisorRoles[selectedAdvisorRole].color" 
                  class="me-1"
                />
                {{ advisorRoles[selectedAdvisorRole].title }}からのアドバイス
              </p>
              <p class="text-body-1 text-grey-darken-3" style="white-space: pre-wrap">{{ advice }}</p>
            </v-sheet>
          </div>
          
          <div v-else>
            <v-sheet class="mx-3 py-3 rounded-lg advisor-container">
              <p class="text-body-1">アドバイザーを選んでください</p>
              
              <v-window v-model="selectedAdvisorRole" show-arrows continuous>
                <v-window-item
                  v-for="(advisor, key) in advisorRoles"
                  :key="key"
                  :value="key"
                >
                  <v-card class="mx-2 bg-transparent" elevation="0">
                    <div class="advisor-image-container d-flex align-end justify-center">
                      <v-img
                        :src="advisor.image"
                        max-height="170"
                        max-width="200"
                        :class="['advisor-image mb-2 mx-auto', { 'scale-up': isButtonHovering || isLoadingAdvice }]"
                        :position="'top'"
                      >
                      </v-img>
                    </div>
                    <v-card-item>
                      <v-card-title class="font-weight-bold">
                        <v-icon
                          :icon="advisor.icon"
                          :color="advisor.color"
                          class="mt-n1 me-2"
                        />
                        {{ advisor.title }}
                      </v-card-title>
                      <v-card-subtitle class="text-body-1 py-2">
                        {{ advisor.description }}
                      </v-card-subtitle>
                    </v-card-item>
                  </v-card>
                </v-window-item>
              </v-window>

              <div class="d-flex justify-center mb-2">
                <v-btn
                  class="px-8"
                  min-width="50%"
                  variant="outlined"
                  @mouseenter="handleButtonHover(true)"
                  @mouseleave="handleButtonHover(false)"
                  @click="handleGenerateAdvice"
                >
                  <template v-if="isLoadingAdvice">
                    <v-progress-circular indeterminate size="18" width="3" :color="advisorRoles[selectedAdvisorRole].color" class="me-2"></v-progress-circular>
                    アドバイザーに相談中...
                  </template>
                  <template v-else>
                    <v-icon icon="mdi-comment-text-outline" class="me-2"></v-icon>
                    このアドバイザーに相談する
                  </template>
                </v-btn>
              </div>
            </v-sheet>
          </div>
        </template>
        <!-- アドバイス機能が無効な場合 -->
        <template v-else>
          <v-img
            :src="advisorRoles[selectedAdvisorRole].image"
            max-width="300"
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
            <v-btn color="error" prepend-icon="mdi-close" variant="elevated" @click="$emit('close')">
              終了する
            </v-btn>
          </v-col>
        </v-row>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useResponsive } from '../composables/useResponsive'
import { advisorRoles, getWeeklyReportAdvice } from '../services/bedrockService'

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
  }
})

const emit = defineEmits(['update:modelValue', 'back', 'close'])

// ローカルの状態管理
const selectedAdvisorRole = ref('manager')
const isButtonHovering = ref(false)
const isLoadingAdvice = ref(false)
const isAdviceAvailable = ref(false)
const advice = ref('')

const resetState = () => {
  selectedAdvisorRole.value = 'manager'
  isLoadingAdvice.value = false
  isAdviceAvailable.value = false
  advice.value = ''
  isButtonHovering.value = false
}

const handleDialogUpdate = (value) => {
  emit('update:modelValue', value)
  if (!value) {
    resetState()
  }
}

watch(() => props.reportContent, (newValue) => {
  if (newValue && Object.keys(newValue).length > 0) {
    resetState()
  }
})

const handleButtonHover = (hovering) => {
  isButtonHovering.value = hovering
}

const handleGenerateAdvice = async () => {
  try {
    if (isLoadingAdvice.value) {
      return
    }

    isLoadingAdvice.value = true
    const result = await getWeeklyReportAdvice({
      ...props.reportContent,
      advisorRole: {
        role: advisorRoles[selectedAdvisorRole.value].role,
        point: advisorRoles[selectedAdvisorRole.value].point
      }
    })
    advice.value = result.advice
    isAdviceAvailable.value = true
  } catch (error) {
    console.error('Error getting weekly report advice:', error)
    advice.value = '申し訳ありません。アドバイスの生成中にエラーが発生しました。'
    isAdviceAvailable.value = true
  } finally {
    isLoadingAdvice.value = false
  }
}
</script>

<style scoped>
.advisor-container {
  border: solid 1px #1e88e5;
  background-color: #e3f2fd;
}

.advisor-image-container {
  height: 175px;
  overflow: hidden;
}

.advisor-image {
  width: 100%;
  transition: transform 0.3s ease;
}

.scale-up {
  transform: scale(1.25);
}

.advisor-image :deep(.v-img__img) {
  object-fit: cover !important;
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
</style>