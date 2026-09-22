"""Embedding 抽象基类。"""

from abc import ABC, abstractmethod
from typing import List


class BaseEmbedding(ABC):
    """向量化接口。

    统一使用 embed_documents / embed_query，便于批量与单条分开优化。
    """

    @property
    @abstractmethod
    def dim(self) -> int:
        """向量维度。"""
        raise NotImplementedError

    @property
    @abstractmethod
    def name(self) -> str:
        """Embedding 名称。"""
        raise NotImplementedError

    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """批量向量化。"""
        raise NotImplementedError

    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """单条查询向量化。"""
        raise NotImplementedError