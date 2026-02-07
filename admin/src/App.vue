<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { useAppStore } from './stores/app'

const appStore = useAppStore()

onMounted(() => {
  if (appStore.isDarkMode) {
    document.documentElement.classList.add('dark')
  }
})

watch(
  () => appStore.isDarkMode,
  (isDark) => {
    if (isDark) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }
)
</script>

<template>
  <router-view />
</template>
