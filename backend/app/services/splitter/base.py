"""切分器抽象基类。"""

from abc import ABC, abstractmethod
from typing import List

from app.models.document import Chunk, Document


class BaseSplitter(ABC):
    """文档切分器基类。"""

    @abstractmethod
    def split(self, document: Document) -> List[Chunk]:
        """将 Document 切分为 Chunk 列表。"""
        raise NotImplementedError
