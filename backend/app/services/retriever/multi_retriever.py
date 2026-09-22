"""多路检索编排：向量 + 关键词 + HyDE → RRF → Rerank → 断崖。

这是 RAG 增强的核心模块。
"""

from typing import Dict, List

from app.core.logger import get_logger
from app.models.document import Chunk, SearchResult
from app.services.reranker import cliff_cutoff, get_reranker
from app.services.retriever.hyde_retriever import HydeRetriever
from app.services.retriever.keyword_retriever import KeywordRetriever
from app.services.retriever.rrf import rrf_fuse
from app.services.vectorstore import get_vector_store

logger = get_logger(__name__)


class MultiRetriever:
    """多路检索编排器。"""

    def __init__(
        self,
        enable_keyword: bool = True,
        enable_hyde: bool = True,
        enable_rerank: bool = True,
        enable_cutoff: bool = True,
        rrf_k: int = 60,
    ) -> None:
        self._store = get_vector_store()
        self._keyword = KeywordRetriever()
        self._hyde = HydeRetriever() if enable_hyde else None
        self._reranker = get_reranker() if enable_rerank else None

        self._enable_keyword = enable_keyword
        self._enable_hyde = enable_hyde
        self._enable_rerank = enable_rerank
        self._enable_cutoff = enable_cutoff
        self._rrf_k = rrf_k

        # 记录已注册到关键词检索的 chunk，避免重复
        self._keyword_chunk_ids: set[str] = set()

    # ------------------------------------------------------------------
    # 索引管理
    # ------------------------------------------------------------------
    def add_chunks(self, chunks: List[Chunk]) -> None:
        """同时注册到向量库和关键词检索。"""
        self._store.add(chunks)

        if self._enable_keyword:
            new_chunks = [c for c in chunks if c.chunk_id not in self._keyword_chunk_ids]
            if new_chunks:
                self._keyword.add_chunks(new_chunks)
                self._keyword_chunk_ids.update(c.chunk_id for c in new_chunks)

    def clear(self) -> None:
        self._store.clear()
        self._keyword.clear()
        self._keyword_chunk_ids.clear()

    # ------------------------------------------------------------------
    # 检索
    # ------------------------------------------------------------------
    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """多路召回 → RRF → Rerank → 断崖。"""
        if not query.strip():
            return []

        # 1. 多路召回
        result_lists: List[List[SearchResult]] = []
        weights: List[float] = []

        # 向量
        vec_results = self._store.search(query, top_k=top_k * 2)
        if vec_results:
            result_lists.append(vec_results)
            weights.append(1.0)

        # 关键词
        if self._enable_keyword:
            kw_results = self._keyword.search(query, top_k=top_k * 2)
            if kw_results:
                result_lists.append(kw_results)
                weights.append(0.8)

        # HyDE
        if self._enable_hyde and self._hyde is not None:
            hyde_results = self._hyde.search(query, top_k=top_k * 2)
            if hyde_results:
                result_lists.append(hyde_results)
                weights.append(1.0)

        if not result_lists:
            return []

        # 2. RRF 融合
        fused = rrf_fuse(result_lists, weights=weights, k=self._rrf_k)
        logger.info("RRF 融合后 %d 条", len(fused))

        # 3. 重排
        if self._enable_rerank and self._reranker is not None:
            reranked = self._reranker.rerank(query, fused, top_k=max(top_k * 2, 10))
        else:
            reranked = fused[: max(top_k * 2, 10)]

        # 4. 断崖检测
        if self._enable_cutoff:
            final = cliff_cutoff(reranked, min_keep=min(3, top_k), max_keep=max(top_k, 5))
        else:
            final = reranked[:top_k]

        logger.info("多路检索最终返回 %d 条", len(final))
        return final