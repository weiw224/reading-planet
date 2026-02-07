<template>
  <div class="not-found">
    <h1>404</h1>
    <p>页面未找到</p>
    <router-link to="/dashboard">返回首页</router-link>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.not-found {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  gap: 1rem;
}

.not-found h1 {
  font-size: 6rem;
  margin: 0;
  color: var(--el-color-primary);
}

.not-found p {
  font-size: 1.5rem;
  color: var(--el-text-color-secondary);
}
</style>
