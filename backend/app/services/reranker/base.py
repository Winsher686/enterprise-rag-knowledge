"""重排器抽象基类。"""

from abc import ABC, abstractmethod
from typing import List

from app.models.document import SearchResult


class BaseReranker(ABC):
    """重排器接口。"""

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def rerank(
        self,
        query: str,
        candidates: List[SearchResult],
        top_k: int = 5,
    ) -> List[SearchResult]:
        """对候选结果重排。"""
        raise NotImplementedError