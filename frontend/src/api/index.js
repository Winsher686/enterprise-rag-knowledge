import axios from 'axios'

const http = axios.create({
  baseURL: '/api',
  timeout: 60000
})

http.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const detail = error?.response?.data?.detail || error.message
    return Promise.reject(new Error(detail))
  }
)

/**
 * 上传文档
 */
export function uploadDocument(file, { title = '', index = true, preferMineru = false } = {}) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('title', title)
  formData.append('index', String(index))
  formData.append('prefer_mineru', String(preferMineru))

  return http.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

/**
 * 同步问答
 */
export function queryRAG(payload) {
  return http.post('/query', payload)
}

/**
 * 健康检查
 */
export function healthCheck() {
  return http.get('/health')
}

/**
 * 流式问答（SSE）
 * 使用 fetch + ReadableStream 解析
 */
export async function queryStream({ query, sessionId, topK = 5, temperature = 0 }, handlers = {}) {
  const { onReady, onDelta, onSources, onFinal, onError } = handlers

  const body = {
    query,
    session_id: sessionId || null,
    top_k: topK,
    temperature
  }

  let response
  try {
    response = await fetch('/api/query/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    })
  } catch (err) {
    onError && onError(err)
    return
  }

  if (!response.ok || !response.body) {
    onError && onError(new Error(`HTTP ${response.status}`))
    return
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder('utf-8')
  let buffer = ''

  try {
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })

      // 按 SSE 事件分割（\n\n）
      let idx
      while ((idx = buffer.indexOf('\n\n')) !== -1) {
        const rawEvent = buffer.slice(0, idx)
        buffer = buffer.slice(idx + 2)
        parseEvent(rawEvent, { onReady, onDelta, onSources, onFinal, onError })
      }
    }
  } catch (err) {
    onError && onError(err)
  }
}

function parseEvent(rawEvent, handlers) {
  const lines = rawEvent.split('\n')
  let event = 'message'
  let dataStr = ''

  for (const line of lines) {
    if (line.startsWith('event:')) {
      event = line.slice(6).trim()
    } else if (line.startsWith('data:')) {
      dataStr += line.slice(5).trim()
    }
  }

  if (!dataStr) return

  let data
  try {
    data = JSON.parse(dataStr)
  } catch {
    return
  }

  const { onReady, onDelta, onSources, onFinal, onError } = handlers

  switch (event) {
    case 'ready':
      onReady && onReady(data)
      break
    case 'delta':
      onDelta && onDelta(data)
      break
    case 'sources':
      onSources && onSources(data)
      break
    case 'final':
      onFinal && onFinal(data)
      break
    case 'error':
      onError && onError(new Error(data.message || '未知错误'))
      break
    default:
      break
  }
}