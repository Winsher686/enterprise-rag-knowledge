"""解析器抽象基类。"""

from abc import ABC, abstractmethod
from typing import Optional

from app.models.document import Document


class BaseParser(ABC):
    """文档解析器基类。"""

    @abstractmethod
    def parse(self, file_path: str, title: Optional[str] = None) -> Document:
        """解析文件，返回 Document。

        Args:
            file_path: 文件路径
            title: 可选标题，若不传则从文件名或内容推断

        Returns:
            Document 对象
        """
        raise NotImplementedError

    @abstractmethod
    def supported_extensions(self) -> list[str]:
        """返回支持的文件扩展名列表，如 ['.md', '.pdf']。"""
        raise NotImplementedError
