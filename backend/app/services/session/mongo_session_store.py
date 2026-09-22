"""MongoDB 会话存储（占位）。

真实使用：
    pip install pymongo
"""

from typing import List, Optional

from app.models.session import Message, Session
from app.services.session.base import BaseSessionStore


class MongoSessionStore(BaseSessionStore):
    """MongoDB 会话存储占位实现。"""

    def __init__(self, uri: str, db_name: str = "enterprise_rag") -> None:
        try:
            from pymongo import MongoClient  # noqa: F401
        except ImportError as exc:
            raise ImportError(
                "使用 MongoDB 会话存储需要安装：pip install pymongo"
            ) from exc
        raise NotImplementedError("MongoSessionStore 将在后续阶段实现")

    def get_or_create(self, session_id: Optional[str] = None) -> Session:
        raise NotImplementedError

    def append(self, session_id: str, message: Message) -> None:
        raise NotImplementedError

    def get_history(self, session_id: str, limit: int = 20) -> List[Message]:
        raise NotImplementedError

    def clear(self, session_id: str) -> None:
        raise NotImplementedError