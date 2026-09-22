<template>
  <el-container class="app-container">
    <el-header class="app-header">
      <div class="logo">
        <el-icon :size="24"><Reading /></el-icon>
        <span class="logo-text">Enterprise RAG Knowledge</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        mode="horizontal"
        router
        class="app-menu"
      >
        <el-menu-item index="/upload">
          <el-icon><Upload /></el-icon>
          <span>文档上传</span>
        </el-menu-item>
        <el-menu-item index="/chat">
          <el-icon><ChatDotRound /></el-icon>
          <span>知识问答</span>
        </el-menu-item>
      </el-menu>
    </el-header>

    <el-main class="app-main">
      <router-view />
    </el-main>

    <el-footer class="app-footer">
      Enterprise RAG Knowledge · MVP v0.1.0
    </el-footer>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const activeMenu = computed(() => route.path)
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #ebeef5;
  background: #fff;
}
.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #409eff;
}
.logo-text {
  font-size: 16px;
}
.app-menu {
  border-bottom: none;
}
.app-main {
  background: #f5f7fa;
  flex: 1;
  padding: 20px;
}
.app-footer {
  text-align: center;
  color: #909399;
  font-size: 12px;
  background: #fff;
  border-top: 1px solid #ebeef5;
}
</style>