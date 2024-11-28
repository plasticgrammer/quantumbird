import { computed } from 'vue'
import { useStore } from 'vuex'
import { WIDGET_DEFINITIONS } from '../store/modules/widget'

export const useWidgets = () => {
  const store = useStore()

  const visibleWidgets = computed(() => 
    store.state.widget.widgetOrder
      .filter(id => store.state.widget.widgetVisibility[id])
  )

  const widgetActions = {
    isExpanded: (id) => computed(() => store.state.widget.expandStates[id]),
    isVisible: (id) => computed(() => store.state.widget.widgetVisibility[id]),
    toggle: (id) => store.dispatch('widget/toggleWidget', id),
    toggleVisibility: (id) => store.dispatch('widget/toggleWidgetVisibility', id),
    updateOrder: (newOrder) => {
      // 表示中のウィジェットのみの並び順を更新
      if (Array.isArray(newOrder) && newOrder.length > 0) {
        const currentVisible = visibleWidgets.value
        if (newOrder.length === currentVisible.length &&
            newOrder.every(id => currentVisible.includes(id))) {
          store.dispatch('widget/updateWidgetOrder', newOrder)
        }
      }
    }
  }

  const getWidgetComponent = (widgetId) => {
    return WIDGET_DEFINITIONS[widgetId]?.component
  }

  return {
    ...widgetActions,
    visibleWidgets,
    widgetOrder: computed(() => store.state.widget.widgetOrder),
    expandStates: computed(() => store.state.widget.expandStates),
    WIDGET_DEFINITIONS,
    getWidgetComponent
  }
}