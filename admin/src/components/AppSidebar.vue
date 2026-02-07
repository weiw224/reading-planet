<template>
  <el-aside width="220px" class="sidebar">
    <div class="logo">
      <span>🌟 阅读星球</span>
    </div>
    
    <el-menu
      :default-active="route.path"
      :router="true"
      background-color="#304156"
      text-color="#bfcbd9"
      active-text-color="#409EFF"
    >
      <el-menu-item index="/dashboard">
        <el-icon><Odometer /></el-icon>
        <span>仪表盘</span>
      </el-menu-item>
      
      <el-sub-menu index="content">
        <template #title>
          <el-icon><Document /></el-icon>
          <span>内容管理</span>
        </template>
        <el-menu-item index="/articles">文章管理</el-menu-item>
        <el-menu-item index="/questions">题目管理</el-menu-item>
      </el-sub-menu>
      
      <el-menu-item index="/users">
        <el-icon><User /></el-icon>
        <span>用户管理</span>
      </el-menu-item>
      
      <el-sub-menu index="settings">
        <template #title>
          <el-icon><Setting /></el-icon>
          <span>系统设置</span>
        </template>
        <el-menu-item index="/settings/tags">标签管理</el-menu-item>
        <el-menu-item index="/settings/badges">勋章管理</el-menu-item>
      </el-sub-menu>
    </el-menu>
  </el-aside>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import { Odometer, Document, User, Setting } from '@element-plus/icons-vue'

const route = useRoute()
</script>

<style scoped>
.sidebar {
  background-color: #304156;
  overflow: hidden;
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 60px;
  background-color: #2b3a4a;
  color: #fff;
  font-size: 18px;
  font-weight: bold;
}

.el-menu {
  border-right: none;
}
</style>
