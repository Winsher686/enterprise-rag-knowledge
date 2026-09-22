"""会话存储工厂。"""

from functools import lru_cache

from app.core.logger import get_logger
from app.services.session.base import BaseSessionStore
from app.services.session.memory_session_store import MemorySessionStore

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def get_session_store() -> BaseSessionStore:
    """返回全局唯一的会话存储。"""
    import os

    provider = os.getenv("SESSION_PROVIDER", "memory").lower()

    if provider == "mongo":
        try:
            from app.core.config import settings
            from app.services.session.mongo_session_store import MongoSessionStore
            logger.info("使用 MongoSessionStore")
            return MongoSessionStore(uri=settings.MONGO_URI, db_name=settings.MONGO_DB)
        except Exception as exc:
            logger.warning("Mongo 会话存储不可用，降级为内存：%s", exc)

    logger.info("使用 MemorySessionStore")
    return MemorySessionStore()


__all__ = ["BaseSessionStore", "MemorySessionStore", "get_session_store"]