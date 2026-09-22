"""统一日志模块。

提供 get_logger()，全项目使用同一套格式和级别。
"""

import logging
import sys

from app.core.config import settings


_LOG_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def _configure_root_logger() -> None:
    """配置根 logger，只执行一次。"""
    root = logging.getLogger()
    if root.handlers:
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(_LOG_FORMAT, _DATE_FORMAT))

    root.addHandler(handler)
    root.setLevel(settings.LOG_LEVEL.upper())


def get_logger(name: str) -> logging.Logger:
    """获取带统一配置的 logger。"""
    _configure_root_logger()
    return logging.getLogger(name)
