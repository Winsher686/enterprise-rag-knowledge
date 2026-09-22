"""解析器工厂。"""

from pathlib import Path

from app.services.parser.base import BaseParser
from app.services.parser.mineru_parser import MinerUParser
from app.services.parser.simple_parser import SimpleParser


def get_parser(file_path: str, prefer_mineru: bool = False) -> BaseParser:
    """根据文件类型返回合适的解析器。

    Args:
        file_path: 文件路径
        prefer_mineru: 是否优先使用 MinerU 解析 PDF
    """
    ext = Path(file_path).suffix.lower()

    if ext == ".pdf" and prefer_mineru:
        return MinerUParser()

    return SimpleParser()


__all__ = ["BaseParser", "SimpleParser", "MinerUParser", "get_parser"]
