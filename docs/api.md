# API 文档

基础路径：`http://localhost:8000`

## 1. 健康检查

### GET /api/health

响应：

```json
{
  "status": "ok",
  "app_name": "enterprise-rag-knowledge",
  "version": "0.1.0",
  "environment": "prod"
}
```



## 2. 上传文档

### POST /api/upload

请求：`multipart/form-data`

| 字段 | 类型 | 必填 | 说明            |
| :--- | :--- | :--- | :-------------- |
| file | File | 是   | Markdown 或 PDF |

响应：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "document_id": "doc_xxx",
    "document_name": "sample.md",
    "chunks_added": 12
  }
}
```



## 3. 提问

### POST /api/query

请求：

```json
{
  "question": "如何上传文档？",
  "session_id": "demo"
}
```



响应：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "answer": "您可以通过前端页面上传 Markdown 或 PDF 文档。",
    "sources": [
      {
        "chunk_id": "chunk_001",
        "document_name": "sample.md",
        "content": "用户可以通过前端页面上传 Markdown 或 PDF 文档。"
      }
    ]
  }
}
```



## 4. SSE 流式提问

### POST /api/query/stream

请求同 `/api/query`。

响应：`text/event-stream`

事件类型：

- `ready`：连接建立
- `delta`：增量内容
- `final`：最终答案 + sources
- `error`：错误信息

示例：

```text
event: ready
data: {"session_id":"demo"}

event: delta
data: {"content":"您可以通过"}

event: delta
data: {"content":"前端页面上传文档。"}

event: final
data: {"answer":"您可以通过前端页面上传文档。","sources":[...]}
```



## 5. 会话管理

### GET /api/session/{session_id}

获取会话历史。

### DELETE /api/session/{session_id}

删除会话。

## 6. 错误码

| code | 说明           |
| :--- | :------------- |
| 0    | 成功           |
| 400  | 请求参数错误   |
| 404  | 资源不存在     |
| 500  | 服务器内部错误 |