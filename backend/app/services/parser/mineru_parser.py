"""MinerU 解析器占位。

MinerU 适合复杂 PDF（表格、公式、多栏），但部署重。
此处仅提供占位，未安装时抛出友好错误。
"""

from pathlib import Path
from typing import Optional

from app.core.logger import get_logger
from app.models.document import Document
from app.services.parser.base import BaseParser

logger = get_logger(__name__)


class MinerUParser(BaseParser):
    """MinerU 解析器占位实现。"""

    def supported_extensions(self) -> list[str]:
        return [".pdf"]

    def parse(self, file_path: str, title: Optional[str] = None) -> Document:
        try:
            import mineru  # noqa: F401
        except ImportError as exc:
            raise ImportError(
                "使用 MinerU 解析器需要安装 mineru，请参考官方文档："
                "https://github.com/opendatalab/MinerU"
            ) from exc

        # 真实实现待阶段 6 接入
        raise NotImplementedError("MinerU 解析器将在后续阶段实现")
