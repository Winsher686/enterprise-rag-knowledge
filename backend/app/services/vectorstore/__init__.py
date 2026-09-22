"""向量库工厂。"""

from functools import lru_cache

from app.core.config import settings
from app.core.logger import get_logger
from app.services.vectorstore.base import BaseVectorStore
from app.services.vectorstore.memory_store import MemoryVectorStore

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def get_vector_store() -> BaseVectorStore:
    """返回全局唯一的向量库实例。

    - VECTOR_STORE=memory → MemoryVectorStore
    - VECTOR_STORE=chroma → ChromaVectorStore（占位）
    - VECTOR_STORE=milvus → MilvusVectorStore（占位）
    - 默认 memory
    """
    provider = (settings.VECTOR_STORE or "memory").lower()

    if provider == "chroma":
        try:
            from app.services.vectorstore.chroma_store import ChromaVectorStore
            logger.info("使用 ChromaVectorStore")
            return ChromaVectorStore()
        except Exception as exc:
            logger.warning("Chroma 不可用，降级为 MemoryVectorStore：%s", exc)

    if provider == "milvus":
        try:
            from app.services.vectorstore.milvus_store import MilvusVectorStore
            logger.info("使用 MilvusVectorStore")
            return MilvusVectorStore()
        except Exception as exc:
            logger.warning("Milvus 不可用，降级为 MemoryVectorStore：%s", exc)

    logger.info("使用 MemoryVectorStore")
    return MemoryVectorStore()


__all__ = ["BaseVectorStore", "MemoryVectorStore", "get_vector_store"]