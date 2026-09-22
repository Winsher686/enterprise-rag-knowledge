"""Markdown 标题层级切分器。

先按 # 标题层级切分，再对过长章节递归切分，最后注入来源标题。
"""

import re
import uuid
from typing import List

from app.core.logger import get_logger
from app.models.document import Chunk, Document
from app.services.splitter.base import BaseSplitter
from app.services.splitter.recursive_splitter import RecursiveCharacterSplitter

logger = get_logger(__name__)

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


class MarkdownSplitter(BaseSplitter):
    """Markdown 智能切分器。"""

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        min_chunk_size: int = 100,
    ) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
        self._recursive = RecursiveCharacterSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    def split(self, document: Document) -> List[Chunk]:
        sections = self._split_by_heading(document.content)
        chunks: List[Chunk] = []

        for section in sections:
            heading = section["heading"] or document.title
            parent = section["parent"]
            body = section["body"].strip()

            if not body:
                continue

            # 短章节：直接作为一个 chunk
            if len(body) <= self.chunk_size:
                chunks.append(self._make_chunk(
                    document=document,
                    title=heading,
                    parent_title=parent,
                    content=body,
                    part=0,
                ))
                continue

            # 长章节：递归切分
            pieces = self._recursive.split_text(body)
            for i, piece in enumerate(pieces):
                if len(piece.strip()) < self.min_chunk_size and i > 0:
                    # 过短片段合并到上一块
                    prev = chunks[-1]
                    prev.raw_content += "\n" + piece.strip()
                    prev.content = self._inject_prefix(prev.title, prev.raw_content)
                    continue
                chunks.append(self._make_chunk(
                    document=document,
                    title=heading,
                    parent_title=parent,
                    content=piece.strip(),
                    part=i,
                ))

        logger.info("文档 %s 切分完成，共 %d 个 chunk", document.doc_id, len(chunks))
        return chunks

    # ------------------------------------------------------------------
    # 内部方法
    # ------------------------------------------------------------------
    @staticmethod
    def _split_by_heading(content: str) -> List[dict]:
        """按 Markdown 标题切分，返回 [{heading, parent, body}, ...]。"""
        lines = content.splitlines()
        sections: List[dict] = []
        current_heading = ""
        current_parent = ""
        current_body: List[str] = []
        heading_stack: List[str] = []

        def flush() -> None:
            if current_body or current_heading:
                sections.append({
                    "heading": current_heading,
                    "parent": current_parent,
                    "body": "\n".join(current_body),
                })

        for line in lines:
            m = _HEADING_RE.match(line)
            if m:
                flush()
                level = len(m.group(1))
                text = m.group(2).strip()

                # 维护标题栈
                heading_stack = heading_stack[:level - 1]
                heading_stack.append(text)

                current_heading = text
                current_parent = heading_stack[-2] if len(heading_stack) >= 2 else ""
                current_body = []
            else:
                current_body.append(line)

        flush()
        return sections

    @staticmethod
    def _inject_prefix(title: str, raw: str) -> str:
        """标题注入：每个 chunk 前加文档来源。"""
        return f"文档来源：{title}\n{raw}"

    def _make_chunk(
        self,
        document: Document,
        title: str,
        parent_title: str,
        content: str,
        part: int,
    ) -> Chunk:
        raw = content.strip()
        injected = self._inject_prefix(title, raw)
        return Chunk(
            chunk_id=f"{document.doc_id}-{uuid.uuid4().hex[:8]}",
            doc_id=document.doc_id,
            content=injected,
            raw_content=raw,
            title=title,
            parent_title=parent_title or None,
            part=part,
            metadata={
                "source": document.source,
                "file_type": document.file_type,
                "doc_title": document.title,
            },
        )
