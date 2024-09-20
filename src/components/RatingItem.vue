<template>
  <v-row class="align-center px-md-6">
    <v-col cols="8" md="3" class="d-flex align-center">
      <span class="text-body-1">{{ label }}</span>
    </v-col>
    <v-col cols="4" md="1" class="d-flex justify-center align-center pa-0">
      <div class="text-h5 mr-5">
        {{ modelValue || '-' }}
        <span class="text-body-1">/ {{ length }}</span>
      </div>
    </v-col>
    <v-col cols="12" md="8" class="d-flex align-middle pa-2">
      <v-rating
        :model-value="modelValue"
        :item-labels="itemLabels"
        :length="length"
        :readonly="readonly"
        :empty-icon="'mdi-emoticon-neutral-outline'"
        :full-icon="fullIcon"
        :half-icon="'mdi-emoticon-neutral-outline'"
        :active-color="negative ? 'blue-lighten-1' : 'orange-accent-3'" 
        size="x-large"
        density="compact"
        color="grey-lighten-2"
        @update:model-value="emit('update:modelValue', $event)"
      ></v-rating>
    </v-col>
  </v-row>
</template>

<script setup>
import { computed } from 'vue'

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
  },
  negative: {
    type: Boolean,
    default: false
  },
  readonly: {
    type: Boolean,
    default: false
  },
})

const fullIcon = computed(() => {
  const half = (props.itemLabels.length + 1) / 2
  if (props.modelValue === half) {
    return 'mdi-emoticon-neutral'
  } else if (props.negative ^ (props.modelValue < half)) {
    return 'mdi-emoticon-dead'
  } else {
    return 'mdi-emoticon'
  }
})

const emit = defineEmits(['update:modelValue'])
</script>

<style>
.v-rating__item .v-btn {
  width: 3.2em;
}

.v-rating__item .v-btn .v-btn__content i {
  transform: scale(1.2);
}
</style>