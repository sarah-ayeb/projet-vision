<script setup>
// Importation des composants
</script>

<template>
  <div class="app-root">
    <router-view />
  </div>
</template>

<style>
/* Global styles */
.app-root {
  width: 100vw;
  max-width: 100vw;
  min-height: 100vh;
  margin: 0;
  padding: 0;
  overflow-x: hidden;
}

html, body {
  width: 100vw;
  max-width: 100vw;
  overflow-x: hidden;
  margin: 0;
  padding: 0;
}

/* Remove any possible black areas */
#app {
  width: 100vw;
  max-width: 100vw;
  background-color: #f8fafc;
  overflow-x: hidden;
}
</style>
