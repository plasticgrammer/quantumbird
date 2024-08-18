<template>
  <v-container>
    <v-row dense class="pb-4">
      <v-col>
        <h3>
          <v-icon size="large" class="mr-1">
            mdi-calendar-multiple-check
          </v-icon>
          週次報告
        </h3>
      </v-col>
    </v-row>

    <ReviewForm
      :week-string="weekString"
    />
  </v-container>
</template>

<script setup>
import ReviewForm from '../components/ReviewForm.vue'

const props = defineProps({
  weekString: {
    type: String,
    default: null
  }
})
</script>