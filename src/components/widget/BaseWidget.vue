<template>
  <v-col 
    :cols="12" 
    :md="expanded ? 12 : 6" 
    class="mb-2 widget-container"
  >
    <v-card class="widget">
      <v-card-title 
        class="text-subtitle-1"
        style="cursor: pointer"
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
  </v-col>
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
  }
})

const store = useStore()

const expanded = computed(() => store.state.widget.expandStates[props.widgetId])

const handleDblClick = () => {
  store.dispatch('widget/toggleWidget', props.widgetId)
}
</script>

<style scoped>
.widget {
  min-height: 165px;
  border-radius: 12px;
}

.widget-container {
  transition: all 0.3s ease-in-out;
}
</style>