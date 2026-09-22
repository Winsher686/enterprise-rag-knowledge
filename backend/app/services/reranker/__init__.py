"""重排器工厂。"""

from functools import lru_cache

from app.core.logger import get_logger
from app.services.reranker.base import BaseReranker
from app.services.reranker.cutoff import cliff_cutoff
from app.services.reranker.noop_reranker import NoopReranker

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def get_reranker() -> BaseReranker:
    """返回全局唯一的重排器。

    - RERANKER_PROVIDER=noop → NoopReranker
    - RERANKER_PROVIDER=qwen → QwenReranker（占位，未实现时降级）
    """
    import os

    provider = os.getenv("RERANKER_PROVIDER", "noop").lower()

    if provider == "qwen":
        try:
            from app.services.reranker.qwen_reranker import QwenReranker
            logger.info("使用 QwenReranker")
            return QwenReranker()
        except Exception as exc:
            logger.warning("QwenReranker 不可用，降级为 NoopReranker：%s", exc)

    logger.info("使用 NoopReranker")
    return NoopReranker()


__all__ = ["BaseReranker", "NoopReranker", "cliff_cutoff", "get_reranker"]