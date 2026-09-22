"""内存向量库：纯 Python 实现，余弦相似度检索。

特点：
- 零依赖
- 适合开发和 CI
- 进程内共享，重启丢失
"""

import math
import threading
from typing import Dict, List, Tuple

from app.core.logger import get_logger
from app.models.document import Chunk, SearchResult
from app.services.embedding import get_embedding
from app.services.vectorstore.base import BaseVectorStore

logger = get_logger(__name__)


class MemoryVectorStore(BaseVectorStore):
    """内存向量库。"""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        # chunk_id -> (chunk, vector)
        self._data: Dict[str, Tuple[Chunk, List[float]]] = {}

    def add(self, chunks: List[Chunk]) -> int:
        if not chunks:
            return 0

        embedding = get_embedding()
        texts = [c.content for c in chunks]
        vectors = embedding.embed_documents(texts)

        with self._lock:
            for chunk, vec in zip(chunks, vectors):
                self._data[chunk.chunk_id] = (chunk, vec)

        logger.info("MemoryVectorStore 写入 %d 条，当前总量 %d", len(chunks), len(self._data))
        return len(chunks)

    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        if not query.strip():
            return []

        embedding = get_embedding()
        q_vec = embedding.embed_query(query)

        with self._lock:
            items = list(self._data.values())

        scored: List[Tuple[float, Chunk]] = []
        for chunk, vec in items:
            score = self._cosine(q_vec, vec)
            scored.append((score, chunk))

        scored.sort(key=lambda x: x[0], reverse=True)
        top = scored[:top_k]

        return [
            SearchResult(
                chunk_id=c.chunk_id,
                doc_id=c.doc_id,
                content=c.content,
                title=c.title,
                score=round(s, 6),
                metadata=c.metadata,
            )
            for s, c in top
        ]

    def clear(self) -> None:
        with self._lock:
            self._data.clear()
        logger.info("MemoryVectorStore 已清空")

    def count(self) -> int:
        with self._lock:
            return len(self._data)

    # ------------------------------------------------------------------
    @staticmethod
    def _cosine(a: List[float], b: List[float]) -> float:
        if not a or not b:
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a)) or 1.0
        nb = math.sqrt(sum(y * y for y in b)) or 1.0
        return dot / (na * nb)