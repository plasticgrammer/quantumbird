<template>
  <v-row>
    <v-col cols="3" class="d-flex align-middle">
      <span class="mt-5">{{ label }}</span>
    </v-col>
    <v-col cols="1" class="d-flex justify-center pa-0">
      <span class="text-h4 mt-5 mr-5">
        {{ modelValue || '-' }}
        <span class="text-h6 ml-n1">/ {{ length }}</span>
      </span>
    </v-col>
    <v-col cols="8" class="d-flex align-middle">
      <v-rating
        :model-value="modelValue"
        :item-labels="itemLabels"
        :length="length"
        size="x-large"
        density="compact"
        @update:model-value="emit('update:modelValue', $event)"
      ></v-rating>
    </v-col>
  </v-row>
</template>

<script setup>
import { ref, defineProps, defineEmits } from 'vue'

const props = defineProps({
  label: {
    type: String,
    required: true
  },
  modelValue: {
    type: Number,
    default: 0
  },
  itemLabels: {
    type: Array,
    default: () => ['', '', '', '', '']
  }
})

const length = ref(props.itemLabels.length)

const emit = defineEmits(['update:modelValue'])
</script>