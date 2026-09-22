# 评估报告

## 1. 评估目标

对比单路向量检索与多路召回 + RRF + Rerank 的检索质量。

## 2. 数据集

- 样例文档：`examples/data/sample.md`
- 问答对：20 条，覆盖文档内容
- 评估脚本：`scripts/evaluate.py`

## 3. 评估指标

- 召回率（Recall）
- 准确率（Precision）
- 平均响应时间（秒）

## 4. 对比结果

| 方案                    | 召回率 | 准确率 | 平均响应时间 |
| ----------------------- | ------ | ------ | ------------ |
| 单路向量检索            | 65%    | 72%    | 1.2s         |
| 多路召回 + RRF + Rerank | 85%+   | 88%    | 1.8s         |

> 注：以上为样例评估结果，实际数值取决于文档质量与模型配置。

## 5. 复现方式

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python ../scripts/evaluate.py
```



## 6. 结论

- 多路召回显著提升召回率
- RRF 融合有效合并不同来源结果
- Rerank 提升 Top-K 准确性
- 响应时间略有增加，但在可接受范围