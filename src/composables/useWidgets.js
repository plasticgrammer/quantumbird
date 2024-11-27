import { ref, computed } from 'vue'
import { useStore } from 'vuex'

export const useWidgets = () => {
  const store = useStore()
  const isReordering = ref(false)
  
  // storeからの値を確実に取得
  const widgetOrder = computed(() => [...store.state.widget.widgetOrder])
  
  const updateOrder = (newOrder) => {
    if (Array.isArray(newOrder) && newOrder.length > 0) {
      store.dispatch('widget/updateWidgetOrder', newOrder)
    }
  }

  const isExpanded = (widgetId) => {
    return computed(() => store.state.widget.expandStates[widgetId])
  }

  const toggleExpand = (widgetId) => {
    store.dispatch('widget/toggleWidget', widgetId)
  }

  return {
    widgetOrder,
    isReordering,
    updateOrder,
    isExpanded,
    toggleExpand
  }
}