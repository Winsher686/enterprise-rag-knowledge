"""内存会话存储。"""

import threading
import time
import uuid
from typing import Dict, List, Optional

from app.core.logger import get_logger
from app.models.session import Message, Session
from app.services.session.base import BaseSessionStore

logger = get_logger(__name__)


class MemorySessionStore(BaseSessionStore):
    """进程内内存会话存储，重启丢失。"""

    def __init__(self, max_messages: int = 100) -> None:
        self._lock = threading.Lock()
        self._sessions: Dict[str, Session] = {}
        self._max_messages = max_messages

    def get_or_create(self, session_id: Optional[str] = None) -> Session:
        with self._lock:
            if session_id and session_id in self._sessions:
                return self._sessions[session_id]

            sid = session_id or uuid.uuid4().hex
            now = time.time()
            session = Session(
                session_id=sid,
                messages=[],
                created_at=now,
                updated_at=now,
            )
            self._sessions[sid] = session
            logger.info("创建会话：%s", sid)
            return session

    def append(self, session_id: str, message: Message) -> None:
        with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                now = time.time()
                session = Session(
                    session_id=session_id,
                    messages=[],
                    created_at=now,
                    updated_at=now,
                )
                self._sessions[session_id] = session

            if message.timestamp <= 0:
                message.timestamp = time.time()
            session.messages.append(message)
            session.updated_at = time.time()

            # 截断，避免无限增长
            if len(session.messages) > self._max_messages:
                session.messages = session.messages[-self._max_messages:]

    def get_history(self, session_id: str, limit: int = 20) -> List[Message]:
        with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                return []
            return list(session.messages[-limit:])

    def clear(self, session_id: str) -> None:
        with self._lock:
            if session_id in self._sessions:
                self._sessions[session_id].messages.clear()
                self._sessions[session_id].updated_at = time.time()