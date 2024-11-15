<template>
  <div id="star-container" class="star-background"></div>
</template>

<script setup>
import { defineProps, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  totalStars: {
    type: Number,
    default: 100
  },
  maxSize: {
    type: Number,
    default: 5
  },
  minSize: {
    type: Number,
    default: 2
  },
  starColor: {
    type: String,
    default: 'white'
  },
  batchSize: {
    type: Number,
    default: 50
  },
  baseSpeed: {
    type: Number,
    default: 3
  },
  speedVariation: {
    type: Number,
    default: 2
  },
  moveUp: {
    type: Boolean,
    default: false
  },
  moveDistance: {
    type: Number,
    default: 100
  }
})

const createStar = () => {
  const starEl = document.createElement('span')
  starEl.className = 'star'
  const size = Math.random() * (props.maxSize - props.minSize) + props.minSize
  const duration = Math.random() * props.speedVariation + props.baseSpeed

  Object.assign(starEl.style, {
    width: `${size}px`,
    height: `${size}px`,
    left: `${Math.random() * 100}%`,
    top: `${Math.random() * 100}%`,
    backgroundColor: props.starColor,
    position: 'absolute',
    borderRadius: '50%',
    animation: props.moveUp 
      ? `starTwinkle ${duration}s ease-in-out infinite, moveUp ${duration}s linear infinite`
      : `starTwinkle ${duration}s ease-in-out infinite`
  })

  return starEl
}

onMounted(() => {
  const container = document.getElementById('star-container')
  if (!container) return

  for (let i = 0; i < props.totalStars; i++) {
    container.appendChild(createStar())
  }
})

onUnmounted(() => {
  const container = document.getElementById('star-container')
  if (container) {
    container.innerHTML = ''
  }
})
</script>

<style>
.star-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  overflow: hidden;
  z-index: -999;
}

.star {
  position: absolute;
  border-radius: 50%;
  opacity: 0;
  transform: scale(0.5);
}

/* 削除: 未使用のスタイル
.star.animate {
  animation: twinkle 3s ease-in-out infinite;
}
*/

@keyframes starTwinkle {
  0% {
    opacity: 0;
    transform: scale(0.5);
  }
  50% {
    opacity: 1;
    transform: scale(1);
  }
  100% {
    opacity: 0;
    transform: scale(0.7);
  }
}

@keyframes moveUp {
  0% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-50px);
  }
  100% {
    transform: translateY(-100px);
  }
}
</style>