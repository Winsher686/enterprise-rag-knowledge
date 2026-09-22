"""关键词检索：Jieba 分词 + Jaccard 相似度。

用于补充向量检索在精确匹配（型号、代码、专有名词）上的不足。
"""

import re
from typing import List, Optional

from app.core.logger import get_logger
from app.models.document import Chunk, SearchResult

logger = get_logger(__name__)

# 中英文分词回退：优先 jieba，未安装则用正则
try:
    import jieba  # type: ignore
    _HAS_JIEBA = True
except ImportError:
    _HAS_JIEBA = False
    logger.warning("未安装 jieba，关键词检索将使用正则分词")


_WORD_RE = re.compile(r"[\u4e00-\u9fa5]|[a-zA-Z0-9]+")


def tokenize(text: str) -> List[str]:
    """分词。"""
    if not text:
        return []
    if _HAS_JIEBA:
        return [w.strip().lower() for w in jieba.cut(text) if w.strip()]
    return [w.lower() for w in _WORD_RE.findall(text)]


def jaccard(a: List[str], b: List[str]) -> float:
    """Jaccard 相似度。"""
    if not a or not b:
        return 0.0
    sa, sb = set(a), set(b)
    inter = len(sa & sb)
    union = len(sa | sb)
    return inter / union if union else 0.0


class KeywordRetriever:
    """关键词检索器。

    这里使用内存中的 chunk 列表，独立于向量库。
    调用方需要先通过 add_chunks() 注册 chunk。
    """

    def __init__(self) -> None:
        self._chunks: List[Chunk] = []
        self._token_cache: List[List[str]] = []

    def add_chunks(self, chunks: List[Chunk]) -> None:
        for chunk in chunks:
            self._chunks.append(chunk)
            self._token_cache.append(tokenize(chunk.content))

    def clear(self) -> None:
        self._chunks.clear()
        self._token_cache.clear()

    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        if not query.strip() or not self._chunks:
            return []

        q_tokens = tokenize(query)
        if not q_tokens:
            return []

        scored: List[tuple[float, int]] = []
        for idx, tokens in enumerate(self._token_cache):
            score = jaccard(q_tokens, tokens)
            if score > 0:
                scored.append((score, idx))

        scored.sort(key=lambda x: x[0], reverse=True)
        top = scored[:top_k]

        results: List[SearchResult] = []
        for score, idx in top:
            chunk = self._chunks[idx]
            results.append(SearchResult(
                chunk_id=chunk.chunk_id,
                doc_id=chunk.doc_id,
                content=chunk.content,
                title=chunk.title,
                score=round(score, 6),
                metadata=chunk.metadata,
            ))
        return results