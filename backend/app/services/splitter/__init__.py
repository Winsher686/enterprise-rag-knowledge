"""切分器工厂。"""

from app.services.splitter.base import BaseSplitter
from app.services.splitter.markdown_splitter import MarkdownSplitter
from app.services.splitter.recursive_splitter import RecursiveCharacterSplitter


def get_splitter(file_type: str = "md") -> BaseSplitter:
    """根据文件类型返回切分器。"""
    if file_type in ("md", "markdown"):
        return MarkdownSplitter()
    return MarkdownSplitter()  # 其他类型也复用 Markdown 逻辑


__all__ = [
    "BaseSplitter",
    "MarkdownSplitter",
    "RecursiveCharacterSplitter",
    "get_splitter",
]
