# RAG 全流程

## 1. 文档上传

- 前端：`POST /api/upload`
- 后端：接收文件，保存到临时目录
- 支持格式：Markdown、PDF

## 2. 文档解析

- Markdown：直接读取
- PDF：PyMuPDF 或 MinerU（可选）
- 输出：纯文本或 Markdown

## 3. 智能切分

- 按 Markdown 标题层级切分
- 过长章节递归切分
- 过短章节合并
- 参数：`chunk_size=1000~1500`，`overlap=200`

## 4. 标题注入

每个 chunk 前添加：

```text
文档来源：{文档标题}
```

目的：切分后仍可追溯来源，避免语义丢失。

## 5. 向量化

- 默认：BGE-M3，生成 dense + sparse 混合向量
- 降级：Mock Embedding
- 批量处理：`batch_size=16`

## 6. 向量入库

- 默认：Chroma
- 可选：Milvus
- 存储内容：向量、chunk_id、文档名、原文

## 7. 多路召回

### 7.1 向量检索

- 用户问题向量化
- 向量库相似度检索
- 返回 Top-K

### 7.2 关键词检索

- Jieba 分词
- Jaccard 相似度
- 粗排 Top-50
- 精排向量余弦相似度

### 7.3 HyDE

- LLM 生成假设答案
- 用户问题 + 假设答案一起向量化
- 再次检索

## 8. RRF 融合

公式：

text

```
score(d) = Σ weight_i / (k + rank_i(d))
```



- `k = 60`
- 融合多路结果，去重排序

## 9. 重排序

- 模型：qwen-rerank / bge-rerank
- 对融合结果精排
- 输出 Top-N

## 10. 断崖检测截断

- 相邻文档分数绝对差 ≥ 0.5 或相对差 ≥ 25% 时截断
- 最少 3 条，最多 10 条
- 动态确定保留数量

## 11. Prompt 构建

- 系统角色：高级技术支持专家
- 参考资料：检索到的 chunk
- 用户问题
- 回答要求：基于事实、不编造、引用来源、无引用拒答

## 12. LLM 生成

- 模型：Qwen3-32B / OpenAI 兼容
- 参数：`temperature=0`
- 输出：Markdown 格式答案

## 13. SSE 流式返回

- 事件类型：`ready`、`delta`、`final`、`error`
- 前端逐块渲染

## 14. 答案溯源

- 响应包含 `sources` 字段
- 每个 source 包含：`chunk_id`、`document_name`、`content`
- 前端可展开查看原文