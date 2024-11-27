<template>
  <div class="widget-container">
    <v-card class="widget">
      <v-card-title 
        class="text-subtitle-1 widget-title"
        @dblclick="handleDblClick"
      >
        <div class="d-flex justify-space-between align-center w-100">
          <div>
            <v-icon 
              small 
              class="mr-1" 
              aria-hidden="true"
            >
              {{ icon }}
            </v-icon>
            {{ title }}
          </div>
          <slot name="header-append"></slot>
        </div>
      </v-card-title>
      <v-card-text :class="contentClass">
        <slot></slot>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup>
import { useStore } from 'vuex'

const props = defineProps({
  widgetId: {
    type: String,
    required: true
  },
  title: {
    type: String,
    required: true
  },
  icon: {
    type: String,
    required: true
  },
  contentClass: {
    type: String,
    default: 'pt-1 pb-3'
  },
  defaultCols: {
    type: Number,
    default: 6
  }
})

const store = useStore()

// const expanded = computed(() => store.state.widget.expandStates[props.widgetId])

const handleDblClick = () => {
  store.dispatch('widget/toggleWidget', props.widgetId)
}
</script>

<style scoped>
.widget {
  min-height: 165px;
  border-radius: 12px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.widget-container {
  transition: all 0.3s ease-in-out;
  height: 100%;
}

.widget :deep(.v-card-text) {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.widget-title {
  cursor: pointer;
  user-select: none;
  /* ドラッグ時のカーソルスタイル */
  &:hover {
    cursor: grab;
  }
  &:active {
    cursor: grabbing;
  }
}
</style>