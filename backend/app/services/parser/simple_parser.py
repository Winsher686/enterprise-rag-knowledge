"""轻量解析器：Markdown / TXT / PDF（可选 pymupdf）。"""

import os
import uuid
from pathlib import Path
from typing import Optional

from app.core.logger import get_logger
from app.models.document import Document
from app.services.parser.base import BaseParser

logger = get_logger(__name__)


class SimpleParser(BaseParser):
    """不依赖重型库的解析器。

    - .md / .txt：直接读取
    - .pdf：若安装了 pymupdf 则解析，否则抛出友好错误
    """

    def supported_extensions(self) -> list[str]:
        return [".md", ".markdown", ".txt", ".pdf"]

    def parse(self, file_path: str, title: Optional[str] = None) -> Document:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"文件不存在：{file_path}")

        ext = path.suffix.lower()
        if ext not in self.supported_extensions():
            raise ValueError(f"不支持的文件类型：{ext}")

        if ext in (".md", ".markdown", ".txt"):
            content = self._read_text(path)
        elif ext == ".pdf":
            content = self._read_pdf(path)
        else:
            raise ValueError(f"不支持的文件类型：{ext}")

        if not content.strip():
            raise ValueError(f"文件内容为空：{file_path}")

        doc_title = title or self._infer_title(path, content)
        doc_id = self._gen_doc_id(path)

        return Document(
            doc_id=doc_id,
            title=doc_title,
            content=content,
            source=path.name,
            file_type=ext.lstrip("."),
            metadata={"path": str(path), "size": path.stat().st_size},
        )

    # ------------------------------------------------------------------
    # 内部方法
    # ------------------------------------------------------------------
    @staticmethod
    def _read_text(path: Path) -> str:
        return path.read_text(encoding="utf-8", errors="ignore")

    @staticmethod
    def _read_pdf(path: Path) -> str:
        try:
            import fitz  # pymupdf
        except ImportError as exc:
            raise ImportError(
                "解析 PDF 需要安装 pymupdf，请执行：pip install pymupdf"
            ) from exc

        logger.info("使用 pymupdf 解析 PDF：%s", path.name)
        texts: list[str] = []
        with fitz.open(str(path)) as doc:
            for page in doc:
                texts.append(page.get_text())
        return "\n\n".join(texts)

    @staticmethod
    def _infer_title(path: Path, content: str) -> str:
        # 优先从 Markdown 一级标题取
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("# "):
                return stripped[2:].strip()
        return path.stem

    @staticmethod
    def _gen_doc_id(path: Path) -> str:
        return f"{path.stem}-{uuid.uuid4().hex[:8]}"
