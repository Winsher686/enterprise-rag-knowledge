"""Milvus 向量库适配器（占位）。

真实使用需要：
    pip install pymilvus
未安装时抛出友好错误。
"""

from typing import List

from app.models.document import Chunk, SearchResult
from app.services.vectorstore.base import BaseVectorStore


class MilvusVectorStore(BaseVectorStore):
    """Milvus 向量库适配器占位。"""

    def __init__(self) -> None:
        try:
            from pymilvus import connections  # noqa: F401
        except ImportError as exc:
            raise ImportError(
                "使用 Milvus 需要安装：pip install pymilvus"
            ) from exc
        raise NotImplementedError("MilvusVectorStore 将在后续阶段实现")

    def add(self, chunks: List[Chunk]) -> int:
        raise NotImplementedError

    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        raise NotImplementedError

    def clear(self) -> None:
        raise NotImplementedError

    def count(self) -> int:
        raise NotImplementedError