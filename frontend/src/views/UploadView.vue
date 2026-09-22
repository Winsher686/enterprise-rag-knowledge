<template>
  <div class="upload-view">
    <el-card class="upload-card">
      <template #header>
        <div class="card-header">
          <el-icon><Upload /></el-icon>
          <span>文档上传</span>
        </div>
      </template>

      <el-form label-width="80px">
        <el-form-item label="文档标题">
          <el-input v-model="title" placeholder="可选，留空自动从内容推断" clearable />
        </el-form-item>
        <el-form-item label="写入向量库">
          <el-switch v-model="indexToStore" />
        </el-form-item>
      </el-form>

      <el-upload
        drag
        :auto-upload="false"
        :show-file-list="false"
        :on-change="handleFileChange"
        :accept="acceptTypes"
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">
          拖拽文件到此处，或 <em>点击选择文件</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持 Markdown / TXT / PDF
          </div>
        </template>
      </el-upload>

      <div class="actions" v-if="selectedFile">
        <el-tag>{{ selectedFile.name }}</el-tag>
        <el-button
          type="primary"
          :loading="uploading"
          @click="doUpload"
        >
          开始上传
        </el-button>
      </div>

      <el-alert
        v-if="errorMsg"
        :title="errorMsg"
        type="error"
        show-icon
        :closable="false"
        class="mt-12"
      />
    </el-card>

    <el-card v-if="result" class="result-card">
      <template #header>
        <div class="card-header">
          <el-icon><DocumentChecked /></el-icon>
          <span>上传结果</span>
        </div>
      </template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="文档标题">{{ result.title }}</el-descriptions-item>
        <el-descriptions-item label="文件类型">{{ result.file_type }}</el-descriptions-item>
        <el-descriptions-item label="文档 ID">{{ result.doc_id }}</el-descriptions-item>
        <el-descriptions-item label="chunk 数量">{{ result.chunk_count }}</el-descriptions-item>
        <el-descriptions-item label="已入库">
          <el-tag :type="result.indexed ? 'success' : 'warning'">
            {{ result.indexed ? '是' : '否' }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>

      <el-divider>chunk 预览</el-divider>
      <el-collapse>
        <el-collapse-item
          v-for="(chunk, idx) in result.chunks.slice(0, 10)"
          :key="chunk.chunk_id"
          :title="`#${idx + 1} ${chunk.title}`"
        >
          <pre class="chunk-content">{{ chunk.content }}</pre>
        </el-collapse-item>
      </el-collapse>
      <div class="mt-12" v-if="result.chunks.length > 10">
        <el-text type="info">仅展示前 10 条，共 {{ result.chunks.length }} 条</el-text>
      </div>

      <div class="mt-16">
        <el-button type="primary" @click="goToChat">去问答</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { uploadDocument } from '../api'

const router = useRouter()

const title = ref('')
const indexToStore = ref(true)
const selectedFile = ref(null)
const uploading = ref(false)
const errorMsg = ref('')
const result = ref(null)

const acceptTypes = '.md,.markdown,.txt,.pdf'

function handleFileChange(file) {
  selectedFile.value = file.raw
  errorMsg.value = ''
}

async function doUpload() {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }

  uploading.value = true
  errorMsg.value = ''
  result.value = null

  try {
    const data = await uploadDocument(selectedFile.value, {
      title: title.value,
      index: indexToStore.value
    })
    result.value = data
    ElMessage.success(`上传成功，共 ${data.chunk_count} 个 chunk`)
  } catch (err) {
    errorMsg.value = err.message || '上传失败'
    ElMessage.error(errorMsg.value)
  } finally {
    uploading.value = false
  }
}

function goToChat() {
  router.push('/chat')
}
</script>

<style scoped>
.upload-view {
  max-width: 960px;
  margin: 0 auto;
}
.upload-card {
  margin-bottom: 16px;
}
.result-card {
  margin-bottom: 16px;
}
.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}
.actions {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 16px;
}
.mt-12 {
  margin-top: 12px;
}
.mt-16 {
  margin-top: 16px;
}
.chunk-content {
  background: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 13px;
  margin: 0;
}
</style>