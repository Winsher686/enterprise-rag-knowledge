"""递归字符切分器。

按分隔符优先级递归切分，控制 chunk_size 和 overlap。
"""

from typing import List

from app.core.logger import get_logger

logger = get_logger(__name__)


class RecursiveCharacterSplitter:
    """递归字符切分器。

    分隔符优先级：段落 > 换行 > 中文句号 > 中文问号 > 中文感叹号 > 空格
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", "。", "？", "！", "；", " ", ""]

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: List[str] | None = None,
    ) -> None:
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap 必须小于 chunk_size")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or self.DEFAULT_SEPARATORS

    def split_text(self, text: str) -> List[str]:
        """切分纯文本。"""
        if not text:
            return []
        return self._split(text, self.separators)

    # ------------------------------------------------------------------
    # 内部递归逻辑
    # ------------------------------------------------------------------
    def _split(self, text: str, separators: List[str]) -> List[str]:
        # 基础情况：文本已足够短
        if len(text) <= self.chunk_size:
            return [text] if text.strip() else []

        # 找到第一个可用的分隔符
        separator = separators[-1]
        for sep in separators:
            if sep == "":
                separator = sep
                break
            if sep in text:
                separator = sep
                break

        # 无分隔符可用：硬切
        if separator == "":
            return self._hard_split(text)

        # 按分隔符切分
        parts = text.split(separator)
        chunks: List[str] = []
        current = ""

        for part in parts:
            candidate = current + (separator if current else "") + part
            if len(candidate) <= self.chunk_size:
                current = candidate
            else:
                if current:
                    chunks.append(current)
                # 单个 part 超长，递归切
                if len(part) > self.chunk_size:
                    next_seps = separators[separators.index(separator) + 1:]
                    chunks.extend(self._split(part, next_seps or [""]))
                    current = ""
                else:
                    current = part

        if current:
            chunks.append(current)

        # 添加 overlap
        return self._add_overlap(chunks)

    def _hard_split(self, text: str) -> List[str]:
        chunks: List[str] = []
        step = self.chunk_size - self.chunk_overlap
        for i in range(0, len(text), step):
            chunks.append(text[i:i + self.chunk_size])
        return chunks

    def _add_overlap(self, chunks: List[str]) -> List[str]:
        if self.chunk_overlap <= 0 or len(chunks) <= 1:
            return chunks

        result = [chunks[0]]
        for i in range(1, len(chunks)):
            prev = result[-1]
            overlap_text = prev[-self.chunk_overlap:] if len(prev) > self.chunk_overlap else prev
            result.append(overlap_text + chunks[i])
        return result
