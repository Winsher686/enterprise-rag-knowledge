"""Embedding 工厂。"""

from functools import lru_cache

from app.core.config import settings
from app.core.logger import get_logger
from app.services.embedding.base import BaseEmbedding
from app.services.embedding.mock_embedding import MockEmbedding

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def get_embedding() -> BaseEmbedding:
    """返回全局唯一的 Embedding 实例。

    优先使用 BGE-M3；不可用时降级为 MockEmbedding。
    可通过环境变量 EMBEDDING_PROVIDER=mock 强制使用 Mock。
    """
    import os

    provider = os.getenv("EMBEDDING_PROVIDER", "auto").lower()

    if provider == "mock":
        logger.info("使用 MockEmbedding（显式指定）")
        return MockEmbedding(dim=128)

    if provider == "bge-m3":
        from app.services.embedding.bge_m3_embedding import BGEM3Embedding
        logger.info("使用 BGEM3Embedding")
        return BGEM3Embedding(model_name=settings.EMBEDDING_MODEL, dim=settings.EMBEDDING_DIM)

    # auto：尝试 BGE-M3，失败则 Mock
    try:
        from app.services.embedding.bge_m3_embedding import BGEM3Embedding
        emb = BGEM3Embedding(model_name=settings.EMBEDDING_MODEL, dim=settings.EMBEDDING_DIM)
        logger.info("使用 BGEM3Embedding（auto）")
        return emb
    except Exception as exc:
        logger.warning("BGE-M3 不可用，降级为 MockEmbedding：%s", exc)
        return MockEmbedding(dim=128)


__all__ = ["BaseEmbedding", "MockEmbedding", "get_embedding"]