# 部署文档

## 1. 环境要求

- Docker 24+
- Docker Compose v2
- 可选：NVIDIA GPU（本地部署大模型时）

## 2. 快速启动

```bash
cp .env.example .env
# 编辑 .env
docker compose up -d
```



服务列表：

| 服务     | 端口      | 说明             |
| :------- | :-------- | :--------------- |
| frontend | 5173      | Vue3 前端        |
| backend  | 8000      | FastAPI 后端     |
| chroma   | 8001      | 向量库           |
| mongo    | 27017     | 会话存储         |
| minio    | 9000/9001 | 图片存储（可选） |

## 3. 环境变量

| 变量            | 说明            | 默认值                |
| :-------------- | :-------------- | :-------------------- |
| LLM_API_KEY     | 大模型 API Key  | 空                    |
| LLM_BASE_URL    | 大模型 API 地址 | 空                    |
| LLM_MODEL       | 模型名          | qwen3-32b             |
| EMBEDDING_MODEL | Embedding 模型  | BAAI/bge-m3           |
| VECTOR_STORE    | 向量库类型      | chroma                |
| MILVUS_HOST     | Milvus 地址     | milvus                |
| MILVUS_PORT     | Milvus 端口     | 19530                 |
| MONGO_URI       | MongoDB 连接串  | mongodb://mongo:27017 |
| MINIO_ENDPOINT  | MinIO 地址      | minio:9000            |

## 4. 本地开发

### 后端

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```



### 前端

```bash
cd frontend
npm install
npm run dev
```



## 5. 生产建议

- 向量库替换为 Milvus 集群
- MongoDB 使用副本集
- MinIO 使用分布式部署
- 后端多实例 + Nginx 负载均衡
- 添加 Redis 缓存
- 接入 Prometheus + Grafana 监控

## 6. 常见问题

### 6.1 Docker 启动失败

检查端口占用：

```bash
netstat -ano | findstr 8000
```



### 6.2 前端跨域

开发环境使用 Vite proxy，生产环境使用 Nginx 反向代理。

### 6.3 大模型 API 超时

调整 `.env` 中的超时参数，或使用本地部署。