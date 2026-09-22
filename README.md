# enterprise-rag-knowledge

> 企业知识智能问答平台（Enterprise RAG Knowledge）

基于 RAG 的企业知识问答系统，支持 Markdown / TXT / PDF 上传、智能切分、向量化检索、多路召回、重排、流式问答与答案溯源。

## 项目状态

- 后端 RAG 闭环（上传 → 切分 → 向量化 → 检索 → 生成 → 溯源）
- 多路召回（向量 + 关键词 + HyDE）
- RRF 融合 + 重排 + 断崖检测
- SSE 流式问答 + 多轮会话
- Vue3 前端（上传、问答、来源展示）
- Docker 一键部署 + GitHub Actions CI

## 核心功能

- **文档上传**：Markdown / TXT / PDF
- **智能切分**：Markdown 标题层级 + 递归字符切分 + 标题注入
- **向量化**：BGE-M3 / Mock Embedding（自动降级）
- **向量库**：Milvus / Chroma / 内存（自动降级）
- **多路召回**：向量检索 + 关键词检索 + HyDE
- **融合与重排**：RRF + Qwen-Rerank + 断崖检测
- **生成与流式**：Qwen / OpenAI 兼容接口，SSE
- **答案溯源**：返回引用 chunk，无引用则拒答
- **多轮会话**：MongoDB / 内存会话（自动降级）

## 技术栈

| 层 | 技术 |
|---|---|
| 后端 | FastAPI、Python 3.11 |
| 前端 | Vue3、Element Plus、Vite |
| 向量库 | Milvus / Chroma / 内存 |
| Embedding | BGE-M3 / Mock |
| 大模型 | Qwen3 / OpenAI 兼容 |
| 文档解析 | PyMuPDF / MinerU |
| 关键词检索 | Jieba + Jaccard |
| 部署 | Docker、Docker Compose |
| CI | GitHub Actions |

## 目录结构

```text
enterprise-rag-knowledge/
├─ backend/                     # FastAPI 后端
│  ├─ app/
│  │  ├─ api/                   # 接口层
│  │  ├─ core/                  # 配置 / 日志
│  │  ├─ models/                # Pydantic 模型
│  │  └─ services/              # 领域服务
│  │     ├─ parser/             # 文档解析
│  │     ├─ splitter/           # 切分
│  │     ├─ embedding/          # 向量化
│  │     ├─ vectorstore/        # 向量库
│  │     ├─ retriever/          # 检索（多路 / RRF / HyDE）
│  │     ├─ reranker/           # 重排 / 断崖
│  │     ├─ llm/                # 大模型
│  │     ├─ prompt/             # Prompt 模板
│  │     └─ session/            # 会话
│  ├─ tests/                    # 单元测试
│  ├─ Dockerfile
│  └─ requirements.txt
├─ frontend/                    # Vue3 前端
│  ├─ src/
│  │  ├─ api/                   # 接口封装 + SSE
│  │  ├─ components/            # 组件
│  │  ├─ router/                # 路由
│  │  ├─ styles/                # 样式
│  │  └─ views/                 # 页面
│  ├─ Dockerfile
│  ├─ nginx.conf
│  └─ package.json
├─ docs/                        # 文档
├─ examples/                    # 样例
├─ scripts/                     # 工具脚本
├─ .github/workflows/ci.yml     # CI
├─ docker-compose.yml           # 一键启动
├─ docker-compose.infra.yml     # 可选中间件
├─ Makefile
└─ README.md
```

## 快速开始

### 方式一：Docker 一键启动（推荐）

```bash
cp .env.example .env
docker compose up -d
```

- 前端：http://127.0.0.1:5173
- 后端 API：http://127.0.0.1:8000
- API 文档：http://127.0.0.1:8000/docs

### 方式二：本地开发

后端：

```bash
cd backend
python -m venv .venv
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

前端：

```bash
cd frontend
npm install
npm run dev
```

访问 http://127.0.0.1:5173。

### 方式三：可选中间件

若需启用 Chroma / MongoDB / MinIO：

```bash
docker compose -f docker-compose.yml -f docker-compose.infra.yml up -d
```

## 环境变量

复制 `.env.example` 为 `.env`，按需修改：

| 变量 | 说明 | 默认 |
|---|---|---|
| LLM_PROVIDER | LLM 提供方：mock / openai | mock |
| LLM_API_KEY | LLM API Key | - |
| LLM_BASE_URL | LLM API Base URL | - |
| LLM_MODEL | LLM 模型名 | qwen3-32b |
| EMBEDDING_PROVIDER | Embedding 提供方：mock / bge-m3 / auto | auto |
| VECTOR_STORE | 向量库：memory / chroma / milvus | memory |
| SESSION_PROVIDER | 会话存储：memory / mongo | memory |
| USE_MULTI_RETRIEVER | 是否启用多路召回 | false |
| RERANKER_PROVIDER | 重排器：noop / qwen | noop |

## API 示例

### 上传文档

```bash
curl -X POST http://127.0.0.1:8000/api/upload \
  -F "file=@examples/data/sample.md" \
  -F "index=true"
```

### 问答（同步）

```bash
curl -X POST http://127.0.0.1:8000/api/query \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"支持哪些文件上传？\",\"top_k\":5}"
```

### 问答（流式）

```bash
curl -N -X POST http://127.0.0.1:8000/api/query/stream \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"支持哪些文件上传？\"}"
```

## 测试

```bash
cd backend
pytest -v
```

或在项目根目录：

```bash
make test
```

## Roadmap

- [x] v0.1.0 最小 RAG 闭环
- [x] v0.2.0 多路召回与重排
- [x] v0.3.0 多轮会话与流式
- [x] v0.4.0 Docker 一键部署 + CI
- [ ] v0.5.0 Milvus / MongoDB / BGE-M3 生产接入
- [ ] v0.6.0 NL2SQL 扩展
- [ ] v0.7.0 多智能体扩展
- [ ] v1.0.0 稳定开源版

## 设计要点

- **适配器模式**：解析 / 切分 / Embedding / 向量库 / LLM / 会话均抽象为接口，可自由切换。
- **自动降级**：重型依赖未装时自动降级到 Mock / 内存实现，保证 MVP 可跑。
- **答案溯源**：每条答案返回引用 chunk，无引用则拒答，降低幻觉。
- **多路召回**：向量 + 关键词 + HyDE 三路互补，RRF 融合，重排 + 断崖检测。
- **流式输出**：SSE 事件规范：ready → delta → sources → final。

## License

MIT