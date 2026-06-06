<script setup>
import SearchBar from '@/components/sidebar/SearchBar.vue'
</script>

<template>
  <main class="flex min-h-screen flex-col items-center justify-center">
    <SearchBar :onHomePage="true" />
  </main>
</template>

<style scoped>
main {
  background: url('/src/components/icons/background.png') no-repeat center center;
  background-size: cover;
}
</style>
