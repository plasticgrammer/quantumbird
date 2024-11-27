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

  const visibleWidgets = computed(() => 
    widgetOrder.value.filter(id => store.state.widget.widgetVisibility[id])
  )

  const isVisible = (widgetId) => {
    return computed(() => store.state.widget.widgetVisibility[widgetId])
  }

  const toggleVisibility = (widgetId) => {
    store.dispatch('widget/toggleWidgetVisibility', widgetId)
  }

  return {
    widgetOrder,
    isReordering,
    updateOrder,
    isExpanded,
    toggleExpand,
    visibleWidgets,
    isVisible,
    toggleVisibility
  }
}