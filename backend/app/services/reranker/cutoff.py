"""断崖检测截断。

原理：
    重排后的结果按分数降序排列，逐对检查相邻文档的分数差距。
    如果绝对差距 >= abs_threshold 或相对差距 >= rel_threshold，
    则认为出现"断崖"，在此处截断。

优势：
    - 避免低分文档混入
    - 避免固定 Top-K 的机械性，根据分数分布动态确定保留数量
"""

from typing import List

from app.models.document import SearchResult


def cliff_cutoff(
    results: List[SearchResult],
    abs_threshold: float = 0.5,
    rel_threshold: float = 0.25,
    min_keep: int = 3,
    max_keep: int = 10,
) -> List[SearchResult]:
    """断崖检测截断。

    Args:
        results: 已按分数降序排列的结果
        abs_threshold: 绝对差距阈值
        rel_threshold: 相对差距阈值
        min_keep: 最少保留条数
        max_keep: 最多保留条数

    Returns:
        截断后的结果列表
    """
    if not results:
        return []
    if len(results) <= min_keep:
        return results[:max_keep]

    keep_count = len(results)
    for i in range(1, len(results)):
        prev_score = results[i - 1].score
        curr_score = results[i].score

        abs_diff = prev_score - curr_score
        rel_diff = abs_diff / (abs(prev_score) + 1e-9)

        if abs_diff >= abs_threshold or rel_diff >= rel_threshold:
            keep_count = i
            break

    # 边界约束
    keep_count = max(keep_count, min_keep)
    keep_count = min(keep_count, max_keep)
    keep_count = min(keep_count, len(results))

    return results[:keep_count]