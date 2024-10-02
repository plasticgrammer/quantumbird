import { computed } from 'vue'

const RATING_CONSTANTS = {
  NEUTRAL_ICON: 'mdi-emoticon-neutral',
  NEGATIVE_ICON: 'mdi-emoticon-dead',
  POSITIVE_ICON: 'mdi-emoticon',
  NEUTRAL_COLOR_NEGATIVE: 'blue-lighten-3',
  NEUTRAL_COLOR_POSITIVE: 'deep-orange-lighten-3',
  NEGATIVE_BASE_COLOR: 'blue',
  POSITIVE_BASE_COLOR: 'deep-orange',
  NO_CHANGE_ICON: 'mdi-minus',
  INCREASE_ICON: 'mdi-arrow-top-right',
  DECREASE_ICON: 'mdi-arrow-bottom-right',
  COMPARISON_COLOR: 'blue-grey-lighten-2',
  NO_COMPARISON_LABEL: '比較データなし',
  IMPROVEMENT_LABEL: '前回より好転',
  DECLINE_LABEL: '前回より悪化',
  NO_CHANGE_LABEL: '前回と変化なし'
}

export function useRatingLogic(props) {
  const { modelValue, itemLabels, comparison, negative } = props
  const length = computed(() => itemLabels.length)
  const half = computed(() => (length.value + 1) / 2)

  const fullIcon = computed(() => {
    if (modelValue === 0 || modelValue === half.value) {
      return RATING_CONSTANTS.NEUTRAL_ICON
    } else if (negative ^ (modelValue < half.value)) {
      return RATING_CONSTANTS.NEGATIVE_ICON
    } else {
      return RATING_CONSTANTS.POSITIVE_ICON
    }
  })

  const activeIconColor = computed(() => {
    if (modelValue === 0 || modelValue === half.value) {
      return negative ? RATING_CONSTANTS.NEUTRAL_COLOR_NEGATIVE : RATING_CONSTANTS.NEUTRAL_COLOR_POSITIVE
    }

    const isNegativeSide = negative !== (modelValue < half.value)
    const baseColor = isNegativeSide ? RATING_CONSTANTS.NEGATIVE_BASE_COLOR : RATING_CONSTANTS.POSITIVE_BASE_COLOR
    const intensity = modelValue < half.value ? modelValue : (length.value + 1) - modelValue
    return `${baseColor}-lighten-${intensity}`
  })

  const comparisonIcon = computed(() => {
    if (comparison === null || modelValue === comparison) return RATING_CONSTANTS.NO_CHANGE_ICON
    return modelValue > comparison ? RATING_CONSTANTS.INCREASE_ICON : RATING_CONSTANTS.DECREASE_ICON
  })

  const comparisonColor = RATING_CONSTANTS.COMPARISON_COLOR

  const comparisonLabel = computed(() => {
    if (comparison === null) return RATING_CONSTANTS.NO_COMPARISON_LABEL
    if (modelValue === comparison) return RATING_CONSTANTS.NO_CHANGE_LABEL
    return modelValue > comparison ^ negative ? RATING_CONSTANTS.IMPROVEMENT_LABEL : RATING_CONSTANTS.DECLINE_LABEL
  })

  return {
    length,
    half,
    fullIcon,
    activeIconColor,
    comparisonIcon,
    comparisonColor,
    comparisonLabel
  }
}