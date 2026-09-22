"""向量库抽象基类。"""

from abc import ABC, abstractmethod
from typing import List

from app.models.document import Chunk, SearchResult


class BaseVectorStore(ABC):
    """向量库接口。"""

    @abstractmethod
    def add(self, chunks: List[Chunk]) -> int:
        """写入 chunk，返回写入数量。"""
        raise NotImplementedError

    @abstractmethod
    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """按查询检索 Top-K。"""
        raise NotImplementedError

    @abstractmethod
    def clear(self) -> None:
        """清空。"""
        raise NotImplementedError

    @abstractmethod
    def count(self) -> int:
        """返回已存储数量。"""
        raise NotImplementedError