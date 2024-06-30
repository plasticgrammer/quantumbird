<template>
    <div class="home">
      <WeeklyReport />
    </div>
  </template>
  
  <script>
  import WeeklyReport from '@/components/WeeklyReport.vue'
  
  export default {
    name: 'HomePage',
    components: {
      WeeklyReport
    }
  }
  </script>
  
  <style scoped>
  .home {
    padding: 20px;
  }
  </style>