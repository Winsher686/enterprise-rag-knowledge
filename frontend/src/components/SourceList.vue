<template>
  <div class="source-list" v-if="sources && sources.length">
    <div class="source-title">
      <el-icon><Document /></el-icon>
      <span>引用来源（{{ sources.length }}）</span>
    </div>
    <el-collapse>
      <el-collapse-item
        v-for="(src, idx) in sources"
        :key="src.chunk_id"
        :name="src.chunk_id"
      >
        <template #title>
          <div class="source-header">
            <el-tag size="small" type="info">资料 {{ idx + 1 }}</el-tag>
            <span class="source-name">{{ src.title }}</span>
            <el-tag size="small" type="success">score {{ src.score.toFixed(3) }}</el-tag>
          </div>
        </template>
        <div class="source-snippet">{{ src.snippet }}</div>
        <div class="source-meta">
          <span>chunk_id: {{ src.chunk_id }}</span>
          <span v-if="src.source">文件: {{ src.source }}</span>
        </div>
      </el-collapse-item>
    </el-collapse>
  </div>
</template>

<script setup>
defineProps({
  sources: {
    type: Array,
    default: () => []
  }
})
</script>

<style scoped>
.source-list {
  margin-top: 12px;
  border-top: 1px dashed #dcdfe6;
  padding-top: 8px;
}
.source-title {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #606266;
  font-size: 13px;
  margin-bottom: 6px;
}
.source-header {
  display: flex;
  align-items: center;
  gap: 8px;
}
.source-name {
  font-weight: 500;
  color: #303133;
}
.source-snippet {
  background: #f5f7fa;
  padding: 8px 10px;
  border-radius: 4px;
  font-size: 13px;
  color: #303133;
  white-space: pre-wrap;
  word-break: break-word;
}
.source-meta {
  margin-top: 6px;
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #909399;
}
</style>