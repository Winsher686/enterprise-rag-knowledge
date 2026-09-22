"""会话存储抽象。"""

from abc import ABC, abstractmethod
from typing import List, Optional

from app.models.session import Message, Session


class BaseSessionStore(ABC):
    """会话存储接口。"""

    @abstractmethod
    def get_or_create(self, session_id: Optional[str] = None) -> Session:
        """获取或创建会话。"""
        raise NotImplementedError

    @abstractmethod
    def append(self, session_id: str, message: Message) -> None:
        """追加消息。"""
        raise NotImplementedError

    @abstractmethod
    def get_history(self, session_id: str, limit: int = 20) -> List[Message]:
        """获取历史消息，按时间顺序返回。"""
        raise NotImplementedError

    @abstractmethod
    def clear(self, session_id: str) -> None:
        """清空会话。"""
        raise NotImplementedError