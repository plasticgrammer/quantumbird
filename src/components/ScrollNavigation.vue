<template>
  <div class="scroll-navigation">
    <v-tooltip
      bottom
      :open-on-hover="true"
      :open-on-focus="true"
    >
      <template #activator="{ props: tooltipProps }">
        <div v-bind="tooltipProps">
          <v-btn
            icon
            elevation="2"
            fab
            small
            tabindex="-1"
            color="blue-grey-lighten-4"
            :readonly="currentIndex === 0"
            aria-label="前のレポートへスクロール"
            @click="scrollToReport(-1)"
          >
            <v-icon>mdi-chevron-up</v-icon>
          </v-btn>
        </div>
      </template>
      <span>上矢印キーでも移動できます</span>
    </v-tooltip>

    <div class="nav-item">
      <v-chip
        variant="text"
        color="blue-grey"
        class="position-chip"
        :aria-label="`現在のレポート: ${currentIndex + 1}/${reportRefs.length}`"
      >
        {{ currentIndex + 1 }} / {{ reportRefs.length }}
      </v-chip>
    </div>

    <v-tooltip
      top
      :open-on-hover="true"
      :open-on-focus="true"
    >
      <template #activator="{ props: tooltipProps }">
        <div v-bind="tooltipProps">
          <v-btn
            icon
            elevation="2"
            fab
            small
            tabindex="-1"
            color="blue-grey-lighten-4"
            :readonly="currentIndex === reportRefs.length - 1"
            aria-label="次のレポートへスクロール"
            @click="scrollToReport(1)"
          >
            <v-icon>mdi-chevron-down</v-icon>
          </v-btn>
        </div>
      </template>
      <span>下矢印キーでも移動できます</span>
    </v-tooltip>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'

const props = defineProps({
  reportRefs: {
    type: Array,
    required: true
  }
})

const currentIndex = ref(0)
const isManualScrolling = ref(false)
const lastManualScrollTime = ref(0)

const getElement = (ref) => {
  if (ref && ref.$el) {
    return ref.$el
  }
  if (ref && typeof ref === 'object' && Object.prototype.hasOwnProperty.call(ref, '$el')) {
    return ref.$el
  }
  return ref
}

const scrollToReport = (direction) => {
  let newIndex = currentIndex.value + direction
  if (newIndex >= 0 && newIndex < props.reportRefs.length) {
    const targetEl = getElement(props.reportRefs[newIndex])
    if (targetEl && typeof targetEl.scrollIntoView === 'function') {
      isManualScrolling.value = true
      lastManualScrollTime.value = Date.now()
      targetEl.scrollIntoView({ behavior: 'smooth', block: 'center' })
      setTimeout(() => {
        currentIndex.value = newIndex
        setTimeout(() => {
          isManualScrolling.value = false
        }, 1000) // スクロールアニメーション完了後、1秒間はスクロールイベントを無視
      }, 500)
    }
  }
}

const debounce = (func, wait) => {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

const handleScroll = debounce(() => {
  if (isManualScrolling.value || Date.now() - lastManualScrollTime.value < 1000) {
    return
  }
  const viewportHeight = window.innerHeight
  const viewportCenter = window.scrollY + viewportHeight / 2

  let closestIndex = -1
  let closestDistance = Infinity

  props.reportRefs.forEach((ref, index) => {
    const element = getElement(ref)
    if (element && typeof element.getBoundingClientRect === 'function') {
      const rect = element.getBoundingClientRect()
      const elementCenter = rect.top + rect.height / 2
      const distance = Math.abs(elementCenter - viewportCenter)
      
      if (distance < closestDistance) {
        closestDistance = distance
        closestIndex = index
      }
    }
  })

  if (closestIndex !== -1 && closestIndex !== currentIndex.value) {
    currentIndex.value = closestIndex
  }
}, 100)

const isTextAreaFocused = () => {
  const activeElement = document.activeElement
  return activeElement && (
    activeElement.tagName.toLowerCase() === 'textarea' ||
    (activeElement.tagName.toLowerCase() === 'input' && activeElement.type === 'text')
  )
}

const handleKeyDown = (event) => {
  if (!isTextAreaFocused()) {
    if (event.key === 'ArrowUp') {
      event.preventDefault()
      scrollToReport(-1)
    } else if (event.key === 'ArrowDown') {
      event.preventDefault()
      scrollToReport(1)
    }
  }
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
  window.addEventListener('keydown', handleKeyDown)
  handleScroll()
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
  window.removeEventListener('keydown', handleKeyDown)
})

watch(() => props.reportRefs, () => {
  handleScroll()
}, { deep: true })
</script>

<style scoped>
.scroll-navigation {
  position: fixed;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  z-index: 9999;
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 150px; /* 全体の高さを固定 */
  justify-content: space-between;
}

.nav-item {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 40px; /* ボタンとチップの高さを統一 */
}

.nav-btn {
  width: 40px;
  height: 40px;
}

.position-chip {
  min-width: 60px;
  height: 32px; /* チップの高さを調整 */
  font-size: 14px;
  justify-content: center;
}
</style>