# 技术亮点速记

## 1. 多路召回

- 向量检索（语义匹配）
- 关键词检索（精确匹配）
- HyDE（假设文档检索）
- 三路互补，召回率从 65% 提升至 85%+

## 2. RRF 融合

- 倒数排名融合算法
- `score(d) = Σ weight_i / (k + rank_i(d))`
- `k = 60`，对异常值不敏感

## 3. 重排序

- qwen-rerank / bge-rerank
- Cross-Encoder 精排
- 提升 Top-K 准确性

## 4. 断崖检测截断

- 相邻分数绝对差 ≥ 0.5 或相对差 ≥ 25% 截断
- 最少 3 条，最多 10 条
- 动态确定保留数量

## 5. 标题注入

- 每个 chunk 添加 `文档来源：{标题}`
- 解决切分后语义丢失、来源追溯问题

## 6. SSE 流式输出

- FastAPI StreamingResponse + AsyncGenerator
- 前端 ReadableStream + TextDecoder
- 事件类型：ready / delta / final / error

## 7. 答案溯源

- 返回引用 chunk
- 无引用则拒答
- 前端可展开查看原文

## 8. 适配器模式

- Embedding：Mock / BGE-M3
- 向量库：内存 / Chroma / Milvus
- LLM：Mock / OpenAI 兼容
- Rerank：Noop / Qwen-Rerank

## 9. 工程化

- Docker Compose 一键启动
- GitHub Actions CI
- pytest 单元测试
- ruff 代码检查
