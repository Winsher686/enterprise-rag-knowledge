"""Noop 重排器：不做任何处理，仅截断 Top-K。"""

from typing import List

from app.models.document import SearchResult
from app.services.reranker.base import BaseReranker


class NoopReranker(BaseReranker):
    """无操作重排器。"""

    @property
    def name(self) -> str:
        return "noop-reranker"

    def rerank(
        self,
        query: str,
        candidates: List[SearchResult],
        top_k: int = 5,
    ) -> List[SearchResult]:
        return candidates[:top_k]