"""Qwen Reranker 适配器（占位）。

真实使用需要：
    pip install dashscope
或调用兼容 API。
未安装时抛出友好错误，由工厂自动降级为 NoopReranker。
"""

from typing import List

from app.models.document import SearchResult
from app.services.reranker.base import BaseReranker


class QwenReranker(BaseReranker):
    """Qwen Reranker 占位实现。"""

    def __init__(self, model: str = "qwen3-rerank") -> None:
        self._model = model
        try:
            import httpx  # noqa: F401
        except ImportError as exc:
            raise ImportError("Qwen Reranker 需要 httpx") from exc
        # 真实实现将在生产阶段补全
        raise NotImplementedError("QwenReranker 将在生产阶段实现")

    @property
    def name(self) -> str:
        return self._model

    def rerank(
        self,
        query: str,
        candidates: List[SearchResult],
        top_k: int = 5,
    ) -> List[SearchResult]:
        raise NotImplementedError