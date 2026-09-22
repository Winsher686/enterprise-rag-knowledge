"""RRF（Reciprocal Rank Fusion）倒数排名融合。

公式：
    score(d) = sum( weight_i / (k + rank_i(d)) )
其中：
    - k 是平滑参数，通常 60
    - rank_i(d) 是文档 d 在第 i 路检索结果中的排名（从 1 开始）
    - weight_i 是第 i 路的权重

优势：
    - 不需要考虑不同检索结果的分数量纲差异
    - 对异常值不敏感
"""

from typing import Dict, List

from app.models.document import SearchResult


def rrf_fuse(
    result_lists: List[List[SearchResult]],
    weights: List[float] | None = None,
    k: int = 60,
) -> List[SearchResult]:
    """融合多路检索结果。

    Args:
        result_lists: 多路检索结果
        weights: 每路权重，默认等权
        k: 平滑参数

    Returns:
        融合后的 SearchResult 列表，score 为 RRF 分数
    """
    if not result_lists:
        return []

    if weights is None:
        weights = [1.0] * len(result_lists)
    if len(weights) != len(result_lists):
        raise ValueError("weights 长度必须与 result_lists 一致")

    # chunk_id -> 累计分数
    fused: Dict[str, float] = {}
    # chunk_id -> 第一次出现的 SearchResult
    meta: Dict[str, SearchResult] = {}

    for weight, results in zip(weights, result_lists):
        for rank, item in enumerate(results, start=1):
            score = weight / (k + rank)
            fused[item.chunk_id] = fused.get(item.chunk_id, 0.0) + score
            if item.chunk_id not in meta:
                meta[item.chunk_id] = item

    # 按融合分数降序
    sorted_items = sorted(fused.items(), key=lambda x: x[1], reverse=True)

    output: List[SearchResult] = []
    for chunk_id, score in sorted_items:
        base = meta[chunk_id]
        output.append(SearchResult(
            chunk_id=base.chunk_id,
            doc_id=base.doc_id,
            content=base.content,
            title=base.title,
            score=round(score, 6),
            metadata=base.metadata,
        ))
    return output