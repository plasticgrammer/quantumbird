import { computed, ref } from 'vue'

const RATING_CONSTANTS = {
  NEUTRAL_ICON: 'mdi-emoticon-neutral',
  NEGATIVE_ICON: 'mdi-emoticon-dead',
  POSITIVE_ICON: 'mdi-emoticon',
  NO_CHANGE_ICON: 'mdi-minus',
  INCREASE_ICON: 'mdi-arrow-top-right',
  DECREASE_ICON: 'mdi-arrow-bottom-right',
  COMPARISON_COLOR: 'blue-grey-lighten-2',
  NO_COMPARISON_LABEL: '比較データなし',
  IMPROVEMENT_LABEL: '前回より好転',
  DECLINE_LABEL: '前回より悪化',
  NO_CHANGE_LABEL: '前回と変化なし',
  NEGATIVE_COLOR: '#1976D2',
  POSITIVE_COLOR: '#E91E63'
}

export function useRatingLogic(props) {
  const { modelValue, itemLabels, comparison, negative } = props
  const length = computed(() => itemLabels.length)
  const half = computed(() => (length.value + 1) / 2)

  const fullIcon = ref(RATING_CONSTANTS.NEUTRAL_ICON)
  const activeIconColor = ref(props.negative ? RATING_CONSTANTS.NEUTRAL_COLOR_NEGATIVE : RATING_CONSTANTS.NEUTRAL_COLOR_POSITIVE)

  const calcFullIcon = (value) => {
    if (value === 0 || value === half.value) {
      return RATING_CONSTANTS.NEUTRAL_ICON
    } else if (negative ^ (value < half.value)) {
      return RATING_CONSTANTS.NEGATIVE_ICON
    } else {
      return RATING_CONSTANTS.POSITIVE_ICON
    }
  }

  const calcActiveIconColor = (value) => {
    const positiveColor = RATING_CONSTANTS.POSITIVE_COLOR
    const negativeColor = RATING_CONSTANTS.NEGATIVE_COLOR

    // 0から1の範囲で位置を計算
    const position = (value - 1) / (length.value - 1)

    // 中央値からの距離を計算（0-0.5の範囲）
    const distanceFromCenter = Math.abs(position - 0.5)
    // 中央に近いほど透明に（0.4-0.9の範囲）
    const alpha = 0.4 + distanceFromCenter * 1.0

    // negativeフラグに応じて色の方向を反転
    let startColor, endColor
    if (negative) {
      startColor = positiveColor
      endColor = negativeColor
    } else {
      startColor = negativeColor
      endColor = positiveColor
    }

    return interpolateColor(startColor, endColor, position, alpha)
  }

  const interpolateColor = (color1, color2, factor, fixedAlpha = null) => {
    const hsl1 = rgbToHsl(parseColor(color1))
    const hsl2 = rgbToHsl(parseColor(color2))

    const h = hsl1.h + (hsl2.h - hsl1.h) * factor
    const s = Math.max(hsl1.s, hsl2.s) * 0.9
    // 明度を少し上げて見やすく
    const l = 0.55

    // 固定の透明度を使用
    return hslToRgbaString(h, s, l, fixedAlpha || 0.9)
  }

  const parseColor = (color) => {
    const hex = color.replace('#', '')
    return {
      r: parseInt(hex.substring(0, 2), 16),
      g: parseInt(hex.substring(2, 4), 16),
      b: parseInt(hex.substring(4, 6), 16)
    }
  }

  const rgbToHsl = (rgb) => {
    const r = rgb.r / 255
    const g = rgb.g / 255
    const b = rgb.b / 255
    const max = Math.max(r, g, b)
    const min = Math.min(r, g, b)
    let h, s
    const l = (max + min) / 2

    if (max === min) {
      h = s = 0
    } else {
      const d = max - min
      s = l > 0.5 ? d / (2 - max - min) : d / (max + min)

      if (max === r) {
        h = (g - b) / d + (g < b ? 6 : 0)
      } else if (max === g) {
        h = (b - r) / d + 2
      } else {
        h = (r - g) / d + 4
      }
      h /= 6
    }
    return { h, s, l }
  }

  const hslToRgbaString = (h, s, l, a) => {
    let r, g, b, q, p

    const hue2rgb = (p, q, t) => {
      if (t < 0) t += 1
      if (t > 1) t -= 1
      if (t < 1 / 6) return p + (q - p) * 6 * t
      if (t < 1 / 2) return q
      if (t < 2 / 3) return p + (q - p) * (2 / 3 - t) * 6
      return p
    }

    if (l < 0.5) {
      q = l * (1 + s)
    } else {
      q = l + s - l * s
    }
    p = 2 * l - q

    r = Math.round(hue2rgb(p, q, h + 1 / 3) * 255)
    g = Math.round(hue2rgb(p, q, h) * 255)
    b = Math.round(hue2rgb(p, q, h - 1 / 3) * 255)

    return `rgba(${r}, ${g}, ${b}, ${a})`
  }

  const updateActiveIcon = (value) => {
    fullIcon.value = calcFullIcon(value)
    activeIconColor.value = calcActiveIconColor(value)
  }

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

  const inactiveIconColor = calcActiveIconColor((length.value + 1) / 2)

  return {
    length,
    half,
    fullIcon,
    activeIconColor,
    comparisonIcon,
    comparisonColor,
    comparisonLabel,
    updateActiveIcon,
    inactiveIconColor
  }
}