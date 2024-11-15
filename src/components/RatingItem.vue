<template>
  <v-row class="align-center px-md-6">
    <v-col cols="8" md="3" class="d-flex align-center">
      <span class="text-body-1">{{ label }}</span>
    </v-col>
    <v-col cols="4" md="2" class="d-flex justify-center align-center pa-0">
      <div class="text-h5 mr-5 text-no-wrap">
        {{ modelValue || '-' }}
        <span class="text-body-1">/ {{ length }}</span>
        <span v-if="readonly">
          <v-tooltip v-if="comparison !== null" location="bottom" :close-delay="500">
            <template #activator="{ props: tooltipProps }">
              <v-icon
                v-bind="tooltipProps"
                :color="comparisonColor"
                class="fluctuation-icon ml-3"
                :aria-label="comparisonLabel"
              >
                {{ comparisonIcon }}
              </v-icon>
            </template>
            前回評価: {{ comparison }}<br>
            {{ comparisonLabel }}
          </v-tooltip>
        </span>
      </div>
    </v-col>
    <v-col cols="12" md="7" class="d-flex align-middle pa-2">
      <v-rating
        ref="rating"
        class="custom-rating"
        :class="{ 'rating-negative': negative }"
        :model-value="modelValue"
        :item-labels="itemLabels"
        :length="length"
        :readonly="readonly"
        :empty-icon="'mdi-emoticon-neutral-outline'"
        :full-icon="fullIcon"
        :half-icon="'mdi-emoticon-neutral-outline'"
        :active-color="activeIconColor"
        size="x-large"
        density="compact"
        color="grey-lighten-2"
        :aria-label="`${label}の評価: ${modelValue}/${length}`"
        :style="{
          '--active-icon-color': activeIconColor,
          '--hover-icon-color': modelValue ? activeIconColor : maxActiveIconColor
        }"
        @update:model-value="handleModelValueUpdate"
      ></v-rating>
    </v-col>
  </v-row>
</template>

<script setup>
import { watch, onMounted } from 'vue'
import { useRatingLogic } from '@/composables/useRatingLogic'

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
  comparison: {
    type: Number,
    default: null
  }
})

const emit = defineEmits(['update:modelValue'])

const {
  length,
  fullIcon,
  activeIconColor,
  maxActiveIconColor,
  comparisonIcon,
  comparisonColor,
  comparisonLabel,
  updateActiveIcon
} = useRatingLogic(props)

const handleModelValueUpdate = (newValue) => {
  updateActiveIcon(newValue)
  emit('update:modelValue', newValue)
}

watch(() => props.modelValue, (newValue) => {
  updateActiveIcon(newValue)
})

onMounted(() => {
  updateActiveIcon(props.modelValue)
})
</script>

<style>
.v-rating__item .v-btn {
  width: 3.2em;
}

.v-rating__item .v-btn .v-btn__content i {
  transform: scale(1.2);
}

/* アクティブなアイコンの色設定 */
.v-rating__wrapper:nth-child(-n + var(--active-rating)) .v-rating__item .v-btn .v-icon {
  color: var(--active-icon-color) !important;
}

/* ホバー時のアイコン色変更 */
.v-rating > .v-rating__wrapper:has(~ .v-rating__wrapper:hover) .v-rating__item .v-btn .v-icon,
.v-rating > .v-rating__wrapper:hover .v-rating__item .v-btn .v-icon {
  color: var(--hover-icon-color) !important;
}

.v-rating .v-btn .v-icon {
  transition: color 0.2s ease;
}
</style>

<style scoped>
.fluctuation-icon {
  font-size: 0.875em;
}
</style>