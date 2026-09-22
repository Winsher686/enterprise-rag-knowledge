"""向量库单元测试。"""

from app.models.document import Chunk
from app.services.vectorstore.memory_store import MemoryVectorStore


def _make_chunk(cid: str, text: str) -> Chunk:
    return Chunk(
        chunk_id=cid,
        doc_id="doc-1",
        content=text,
        raw_content=text,
        title="测试标题",
        metadata={"source": "test.md"},
    )


def test_memory_store_add_and_count() -> None:
    store = MemoryVectorStore()
    store.clear()
    assert store.count() == 0

    chunks = [_make_chunk(f"c{i}", f"内容{i}") for i in range(5)]
    added = store.add(chunks)
    assert added == 5
    assert store.count() == 5


def test_memory_store_search() -> None:
    store = MemoryVectorStore()
    store.clear()

    chunks = [
        _make_chunk("c1", "Python 是一种编程语言"),
        _make_chunk("c2", "Java 也是一种编程语言"),
        _make_chunk("c3", "今天天气很好"),
    ]
    store.add(chunks)

    results = store.search("编程语言", top_k=2)
    assert len(results) == 2
    assert all(r.score >= 0 for r in results)


def test_memory_store_search_empty_query() -> None:
    store = MemoryVectorStore()
    store.clear()
    results = store.search("", top_k=5)
    assert results == []


def test_memory_store_clear() -> None:
    store = MemoryVectorStore()
    store.add([_make_chunk("c1", "内容")])
    assert store.count() == 1
    store.clear()
    assert store.count() == 0