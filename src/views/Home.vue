<template>
    <div class="home">
      <WeekSelector />
    </div>
  </template>
  
  <script>
  import WeekSelector from '@/components/WeekSelector.vue'
  
  export default {
    name: 'HomePage',
    components: {
      WeekSelector
    }
  }
  </script>
  
  <style scoped>
  .home {
    padding: 20px;
  }
  
  h1 {
    text-align: center;
    margin-bottom: 20px;
  }
  </style>