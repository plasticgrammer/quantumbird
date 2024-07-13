<template>
  <v-app id="main">
    <v-main>
      <router-view/>
    </v-main>
  </v-app>
</template>

<script>
export default {
  name: 'App',

  data: () => ({
    //
  }),
}
</script>

<style scoped>
#main {
  max-width: 960px;
  margin: 0 auto;
}
</style>
