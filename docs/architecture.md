# 架构设计

## 1. 总体架构

企业知识智能问答平台采用前后端分离架构：

- **前端**：Vue3 + Element Plus + Vite
- **后端**：FastAPI + LangGraph
- **向量库**：Milvus / Chroma
- **Embedding**：BGE-M3
- **大模型**：Qwen3 / OpenAI 兼容接口
- **存储**：MongoDB、MinIO（可选）
- **部署**：Docker、Docker Compose

## 2. 模块划分

### 2.1 前端模块

- 文档上传
- 问答聊天
- Markdown 渲染
- 来源 chunk 展示
- SSE 流式接收

### 2.2 后端模块

| 模块                    | 职责                     |
| ----------------------- | ------------------------ |
| `api/`                  | 路由，参数校验，响应封装 |
| `core/`                 | 配置、日志、异常         |
| `models/`               | Pydantic 请求/响应模型   |
| `services/parser/`      | 文档解析                 |
| `services/splitter/`    | 文档切分、标题注入       |
| `services/embedding/`   | 向量化                   |
| `services/vectorstore/` | 向量库适配               |
| `services/retriever/`   | 多路召回、RRF、重排      |
| `services/reranker/`    | 重排序                   |
| `services/llm/`         | LLM 调用                 |
| `services/prompt/`      | Prompt 模板              |
| `services/session/`     | 多轮会话                 |
| `graph/`                | LangGraph 编排           |

## 3. 数据流

1. 用户上传文档
2. 后端解析文档为 Markdown/文本
3. 智能切分 + 标题注入
4. 向量化并写入向量库
5. 用户提问
6. 多路召回：向量检索、关键词检索、HyDE
7. RRF 融合
8. Rerank 精排
9. 断崖检测截断
10. Prompt 构建
11. LLM 生成答案
12. SSE 流式返回
13. 答案引用 chunk，无引用拒答

## 4. 关键设计

### 4.1 适配器模式

所有重型组件均提供适配器：

- Embedding：Mock / BGE-M3
- 向量库：内存 / Chroma / Milvus
- LLM：Mock / OpenAI 兼容
- Rerank：Noop / Qwen-Rerank

保证无 GPU、无外部服务也能跑通 MVP。

### 4.2 答案溯源

每个 chunk 带有 `chunk_id`、文档名、原文片段。  
生成答案时要求 LLM 引用来源，无引用则返回“未在知识库中找到依据”。

### 4.3 流式输出

后端使用 FastAPI `StreamingResponse` + `AsyncGenerator`，  
前端使用 `ReadableStream` + `TextDecoder` 逐块解析。

## 5. 部署架构

- Docker Compose 编排 backend、frontend、chroma、mongo、minio
- 生产环境可替换为 Milvus 集群、独立 MongoDB、MinIO 集群
- CI 使用 GitHub Actions，执行 ruff、pytest、frontend build
