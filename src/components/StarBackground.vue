// StarBackground.vue
<template>
  <div id="star-container" class="star-background"></div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'

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
  }
})

// 星を生成する関数
const createStar = () => {
  const starEl = document.createElement('span')
  starEl.className = 'star'
  const size = Math.random() * (props.maxSize - props.minSize) + props.minSize

  Object.assign(starEl.style, {
    width: `${size}px`,
    height: `${size}px`,
    left: `${Math.random() * 100}%`,
    top: `${Math.random() * 100}%`,
    animationDelay: `${Math.random() * 5}s`,
    position: 'absolute',
    backgroundColor: props.starColor,
    borderRadius: '50%',
    opacity: Math.random()
  })

  return starEl
}

// バッチ処理で星を生成する関数
const createStarsInBatches = () => {
  const container = document.getElementById('star-container')
  if (!container) return

  for (let i = 0; i < props.totalStars; i += props.batchSize) {
    requestAnimationFrame(() => {
      const batchFragment = document.createDocumentFragment()
      const limit = Math.min(i + props.batchSize, props.totalStars)

      for (let j = i; j < limit; j++) {
        batchFragment.appendChild(createStar())
      }

      container.appendChild(batchFragment)
    })
  }
}

onMounted(() => {
  setTimeout(() => {
    createStarsInBatches()
  }, 100)
})

onUnmounted(() => {
  const container = document.getElementById('star-container')
  if (container) {
    container.innerHTML = ''
  }
})
</script>

<style scoped>
.star-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  pointer-events: none;
  overflow: hidden;
  z-index: -999;
}

.star {
  position: absolute;
  animation: twinkle 5s infinite;
}

@keyframes twinkle {
  0% { opacity: 0; }
  50% { opacity: 1; }
  100% { opacity: 0; }
}
</style>