"""会话存储测试。"""

from app.models.session import Message
from app.services.session.memory_session_store import MemorySessionStore


def test_create_session() -> None:
    store = MemorySessionStore()
    session = store.get_or_create()
    assert session.session_id
    assert session.messages == []


def test_get_existing_session() -> None:
    store = MemorySessionStore()
    s1 = store.get_or_create("sid-1")
    s2 = store.get_or_create("sid-1")
    assert s1.session_id == s2.session_id


def test_append_and_history() -> None:
    store = MemorySessionStore()
    store.get_or_create("sid-2")
    store.append("sid-2", Message(role="user", content="你好"))
    store.append("sid-2", Message(role="assistant", content="你好，有什么可以帮您？"))

    history = store.get_history("sid-2")
    assert len(history) == 2
    assert history[0].role == "user"
    assert history[1].role == "assistant"


def test_clear_session() -> None:
    store = MemorySessionStore()
    store.get_or_create("sid-3")
    store.append("sid-3", Message(role="user", content="测试"))
    store.clear("sid-3")
    assert store.get_history("sid-3") == []