import { computed } from 'vue'
import { useDisplay } from 'vuetify'

export function useResponsive() {
  const { smAndDown, width } = useDisplay()

  const isMobile = computed(() => {
    // 640px未満をモバイルとして扱う
    return width.value < 640
  })

  const isTablet = computed(() => {
    // 640px以上、1024px未満をタブレットとして扱う
    return width.value >= 640 && width.value < 1024
  })

  const isDesktop = computed(() => {
    // 1024px以上をデスクトップとして扱う
    return width.value >= 1024
  })

  return {
    isMobile,
    isTablet,
    isDesktop,
    smAndDown
  }
}