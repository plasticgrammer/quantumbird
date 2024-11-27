import { ref, computed } from 'vue'
import { useStore } from 'vuex'

// ウィジェット定義の型
const WIDGET_DEFINITIONS = {
  calendar: {
    component: 'CalendarWidget',
    title: '報告状況'
  },
  overtime: {
    component: 'StatsWidget',
    title: '残業時間の遷移'
  },
  stress: {
    component: 'StatsWidget',
    title: 'ストレス評価の遷移'
  },
  organization: {
    component: 'OrganizationWidget',
    title: '組織情報'
  },
  reportRequest: {
    component: 'ReportRequestWidget',
    title: '報告依頼'
  },
  todo: {
    component: 'TodoListWidget',
    title: 'やることリスト'
  },
  weeklyReport: {
    component: 'WeeklyReportWidget',
    title: 'メンバーの週次報告'
  },
  disability: {
    component: 'StatsWidget',
    title: 'タスク難易度の遷移'
  },
  achievement: {
    component: 'StatsWidget',
    title: 'タスク達成度の遷移'
  }
}

export const useWidgets = () => {
  const store = useStore()
  const isReordering = ref(false)

  // ストアからwidgetOrderを取得
  const widgetOrder = computed(() => store.state.widget.widgetOrder)

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

  const getWidgetDefinition = (widgetId) => {
    return WIDGET_DEFINITIONS[widgetId]
  }

  const getWidgetComponent = (widgetId) => {
    return WIDGET_DEFINITIONS[widgetId]?.component
  }

  const getWidgetTitle = (widgetId) => {
    return WIDGET_DEFINITIONS[widgetId]?.title
  }

  return {
    widgetOrder,
    isReordering,
    updateOrder,
    isExpanded,
    toggleExpand,
    visibleWidgets,
    isVisible,
    toggleVisibility,
    getWidgetDefinition,
    getWidgetComponent,
    getWidgetTitle,
    WIDGET_DEFINITIONS
  }
}