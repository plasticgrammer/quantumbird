<template>
  <v-card class="mt-2" variant="text" elevation="0">
    <v-card-text class="d-flex align-center pa-2">
      <v-icon :color="getOvertimeColor" class="mr-2" size="24">mdi-clock-outline</v-icon>
      <div class="overtime-info flex-grow-1">
        <div class="d-flex align-center">
          <span class="text-subtitle-2 mr-2 mt-1">残業時間:</span>
          <span v-if="overtimeHours === 0" class="text-body-1 font-weight-bold">
            なし
          </span>
          <template v-else>
            <span class="text-body-1 font-weight-bold" :class="getOvertimeColor">
              {{ overtimeHours }}時間
            </span>
          </template>
        </div>
        <v-progress-linear
          :model-value="getOvertimePercentage"
          :color="getOvertimeColor"
          height="10"
          rounded
          class="w-75 opacity-80 mt-1"
        ></v-progress-linear>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  overtimeHours: {
    type: Number,
    required: true
  }
})

const maxValue = 15

const getOvertimeColor = computed(() => {
  if (props.overtimeHours === 0) return 'blue'
  if (props.overtimeHours <= maxValue / 2) return 'blue-accent-1'
  if (props.overtimeHours <= maxValue) return 'warning'
  return 'error'
})

const getOvertimePercentage = computed(() => {
  return Math.min(props.overtimeHours / maxValue * 100, 100)
})
</script>

<style scoped>
.overtime-info {
  display: flex;
  flex-direction: column;
  justify-content: center;
}
</style>