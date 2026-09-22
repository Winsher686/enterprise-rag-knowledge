<template>
  <div class="chat-view">
    <el-card class="chat-card">
      <template #header>
        <div class="card-header">
          <el-icon><ChatDotRound /></el-icon>
          <span>知识问答</span>
          <el-tag v-if="sessionId" size="small" type="info" class="session-tag">
            session: {{ sessionId.slice(0, 8) }}
          </el-tag>
          <div class="header-actions">
            <el-button size="small" @click="clearMessages">清空</el-button>
          </div>
        </div>
      </template>

      <div ref="messagesRef" class="messages">
        <el-empty v-if="!messages.length" description="上传文档后开始提问" />

        <div
          v-for="(msg, idx) in messages"
          :key="idx"
          class="message"
          :class="`message-${msg.role}`"
        >
          <div class="message-avatar">
            <el-icon v-if="msg.role === 'user'"><User /></el-icon>
            <el-icon v-else><MagicStick /></el-icon>
          </div>
          <div class="message-body">
            <div
              v-if="msg.role === 'assistant'"
              class="markdown-body"
              v-html="renderMarkdown(msg.content)"
            ></div>
            <div v-else class="user-text">{{ msg.content }}</div>

            <SourceList
              v-if="msg.role === 'assistant' && msg.sources && msg.sources.length"
              :sources="msg.sources"
            />
          </div>
        </div>

        <div v-if="streaming" class="message message-assistant">
          <div class="message-avatar">
            <el-icon><MagicStick /></el-icon>
          </div>
          <div class="message-body">
            <div class="markdown-body" v-html="renderMarkdown(streamingText)"></div>
            <div class="streaming-indicator">▍</div>
          </div>
        </div>
      </div>

      <div class="input-area">
        <el-input
          v-model="inputText"
          type="textarea"
          :rows="2"
          placeholder="输入问题，例如：支持哪些文件上传？"
          :disabled="streaming"
          @keydown.enter.exact.prevent="send"
        />
        <div class="input-actions">
          <el-input-number v-model="topK" :min="1" :max="20" size="small" />
          <el-button
            type="primary"
            :loading="streaming"
            :disabled="!inputText.trim()"
            @click="send"
          >
            发送
          </el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { nextTick, ref } from 'vue'
import { marked } from 'marked'
import { ElMessage } from 'element-plus'
import { queryStream } from '../api'
import SourceList from '../components/SourceList.vue'

const messages = ref([])
const inputText = ref('')
const streaming = ref(false)
const streamingText = ref('')
const sessionId = ref('')
const topK = ref(5)
const messagesRef = ref(null)

marked.setOptions({ breaks: true, gfm: true })

function renderMarkdown(text) {
  if (!text) return ''
  try {
    return marked.parse(text)
  } catch {
    return text
  }
}

async function scrollToBottom() {
  await nextTick()
  const el = messagesRef.value
  if (el) el.scrollTop = el.scrollHeight
}

function clearMessages() {
  messages.value = []
  streamingText.value = ''
}

async function send() {
  const query = inputText.value.trim()
  if (!query) return

  messages.value.push({ role: 'user', content: query })
  inputText.value = ''
  streaming.value = true
  streamingText.value = ''
  await scrollToBottom()

  let currentSources = []
  let fullAnswer = ''

  await queryStream(
    { query, sessionId: sessionId.value, topK: topK.value },
    {
      onReady(data) {
        if (data.session_id) sessionId.value = data.session_id
      },
      onDelta(data) {
        streamingText.value += data.text || ''
        scrollToBottom()
      },
      onSources(data) {
        currentSources = data.sources || []
      },
      onFinal(data) {
        fullAnswer = data.answer || streamingText.value
        messages.value.push({
          role: 'assistant',
          content: fullAnswer,
          sources: currentSources
        })
        streamingText.value = ''
        streaming.value = false
        scrollToBottom()
      },
      onError(err) {
        ElMessage.error(err.message || '流式问答失败')
        streaming.value = false
      }
    }
  )
}
</script>

<style scoped>
.chat-view {
  max-width: 960px;
  margin: 0 auto;
  height: calc(100vh - 140px);
  display: flex;
}
.chat-card {
  width: 100%;
  display: flex;
  flex-direction: column;
}
.chat-card :deep(.el-card__body) {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}
.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}
.session-tag {
  margin-left: 8px;
}
.header-actions {
  margin-left: auto;
}
.messages {
  flex: 1;
  overflow-y: auto;
  padding: 12px 4px;
}
.message {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
}
.message-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #ecf5ff;
  color: #409eff;
  flex-shrink: 0;
}
.message-user .message-avatar {
  background: #f0f9eb;
  color: #67c23a;
}
.message-body {
  flex: 1;
  min-width: 0;
}
.user-text {
  background: #f0f9eb;
  padding: 8px 12px;
  border-radius: 6px;
  white-space: pre-wrap;
  word-break: break-word;
}
.input-area {
  border-top: 1px solid #ebeef5;
  padding-top: 12px;
}
.input-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 8px;
  justify-content: flex-end;
}
.streaming-indicator {
  color: #409eff;
  animation: blink 1s infinite;
}
@keyframes blink {
  50% { opacity: 0; }
}
</style>