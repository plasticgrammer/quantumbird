<template>
  <div class="widget-wrapper" :class="{ 'widget-expanded': expanded }">
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
import { computed } from 'vue'
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

const expanded = computed(() => store.state.widget.expandStates[props.widgetId])

const handleDblClick = () => {
  store.dispatch('widget/toggleWidget', props.widgetId)
}
</script>

<style scoped>
.widget-wrapper {
  padding: 8px;
  width: 50%;
  transition: all 0.3s ease-in-out;
}

.widget-wrapper.widget-expanded {
  width: 100%;
}

.widget {
  min-height: 165px;
  height: 100%;
  border-radius: 12px;
}

.widget-container {
  transition: all 0.3s ease-in-out;
}

.widget-title {
  cursor: pointer;
  user-select: none;
}
</style>