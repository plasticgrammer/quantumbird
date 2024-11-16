<template>
  <v-dialog
    :model-value="modelValue"
    max-width="400"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <v-card class="completion-dialog rounded-xl">
      <div class="completion-background">
        <div class="ripple-effect" />
      </div>
      <v-card-text class="text-center pa-8 pb-2">
        <div class="completion-icon-wrapper mb-8">
          <v-icon
            icon="mdi-check-circle"
            color="info"
            size="80"
            class="completion-icon"
          />
          <div class="completion-icon-ring" />
          <div class="completion-icon-ring delay-1" />
          <div class="completion-icon-ring delay-2" />
        </div>
        <div class="text-h5 font-weight-bold mb-5 completion-title">
          すべての報告を確認しました！
        </div>
        <div class="text-body-1 text-grey-darken-2 mb-2 fade-in-up delay-1">
          メンバー{{ reportCount }}名の週次報告確認が完了しました
        </div>
        <div class="text-subtitle-1 text-grey-darken-1 fade-in-up delay-2">
          おつかれさまでした<v-icon color="amber-accent-3" class="ml-1 mt-n1">mdi-emoticon-happy-outline</v-icon>
        </div>
      </v-card-text>
      <v-card-actions class="pa-4 d-flex flex-column">
        <v-btn
          color="secondary"
          size="large"
          class="px-6 fade-in-up delay-3 mb-2 w-100"
          @click="$emit('share')"
        >
          共有する
          <v-icon class="ml-2">
            mdi-share-variant
          </v-icon>
        </v-btn>
        <v-btn
          color="primary"
          size="large"
          class="px-6 fade-in-up delay-3 w-100"
          @click="$emit('update:modelValue', false)"
        >
          閉じる ({{ countdown }}秒)
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, onBeforeUnmount, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true
  },
  reportCount: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['update:modelValue', 'share'])

const countdown = ref(10)
let timer

const startCountdown = () => {
  if (timer) {
    clearInterval(timer)
  }
  countdown.value = 10
  timer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearInterval(timer)
      emit('update:modelValue', false)
    }
  }, 1000)
}

watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    startCountdown()
  } else {
    if (timer) {
      clearInterval(timer)
    }
  }
})

onBeforeUnmount(() => {
  if (timer) {
    clearInterval(timer)
  }
})
</script>

<style scoped>
.completion-dialog {
  background: linear-gradient(165deg, #ffffff 0%, #f8fbff 100%);
  position: relative;
  overflow-y: hidden !important;
}

.completion-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 160px;
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  opacity: 0.1;
  overflow: hidden;
}

.ripple-effect {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 200%;
  padding-bottom: 200%;
  transform: translate(-50%, -50%);
  background: radial-gradient(circle, rgba(3, 169, 244, 0.1) 0%, transparent 70%);
  animation: ripple 3s ease-out infinite;
}

.completion-icon-wrapper {
  position: relative;
  display: inline-block;
}

.completion-icon {
  position: relative;
  z-index: 2;
  animation: bounceIn 0.8s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.completion-icon-ring {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 86px;
  height: 86px;
  border-radius: 50%;
  transform: translate(-50%, -50%);
  border: 3px solid #0288d1;
  opacity: 0;
  animation: ringPulse 1.5s ease-out 0.4s forwards;
}

.completion-icon-ring.delay-1 {
  animation: ringPulse 1.5s ease-out 0.8s infinite;
}

.completion-icon-ring.delay-2 {
  animation: ringPulse 1.5s ease-out 1.2s infinite;
}

.completion-title {
  background: linear-gradient(45deg, #2962ff, #448aff);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  animation: slideIn 0.5s ease-out 0.2s both;
}

.fade-in-up {
  opacity: 0;
  animation: fadeInUp 0.6s ease-out forwards;
}

.fade-in-up.delay-1 {
  animation-delay: 0.3s;
}

.fade-in-up.delay-2 {
  animation-delay: 0.5s;
}

.fade-in-up.delay-3 {
  animation-delay: 0.7s;
}

@keyframes bounceIn {
  0% {
    transform: scale(0);
    opacity: 0;
  }
  50% {
    transform: scale(1.2);
  }
  70% {
    transform: scale(0.9);
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

@keyframes ringPulse {
  0% {
    transform: translate(-50%, -50%) scale(0.8);
    opacity: 0;
  }
  50% {
    opacity: 0.5;
  }
  100% {
    transform: translate(-50%, -50%) scale(1.2);
    opacity: 0;
  }
}

@keyframes slideIn {
  0% {
    transform: translateY(20px);
    opacity: 0;
  }
  100% {
    transform: translateY(0);
    opacity: 1;
  }
}

@keyframes ripple {
  0% {
    transform: translate(-50%, -50%) scale(0);
    opacity: 0.5;
  }
  100% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 0;
  }
}

@keyframes fadeInUp {
  0% {
    transform: translateY(20px);
    opacity: 0;
  }
  100% {
    transform: translateY(0);
    opacity: 1;
  }
}

.w-100 {
  width: 100%;
}
</style>