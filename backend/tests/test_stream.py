"""流式与多轮测试。"""

from app.models.document import Chunk
from app.models.session import Message
from app.services.retriever import RAGRetriever
from app.services.vectorstore import get_vector_store


def _make_chunk(cid: str, content: str) -> Chunk:
    return Chunk(
        chunk_id=cid,
        doc_id="doc-1",
        content=content,
        raw_content=content,
        title="测试文档",
        metadata={"source": "test.md"},
    )


def _prepare_store():
    store = get_vector_store()
    store.clear()
    store.add([
        _make_chunk("c1", "企业知识库支持 Markdown 和 PDF 上传。"),
        _make_chunk("c2", "用户可以用自然语言提问。"),
        _make_chunk("c3", "系统返回答案并附带引用来源。"),
    ])
    return store


def test_answer_stream_with_context() -> None:
    _prepare_store()
    retriever = RAGRetriever()
    deltas = list(retriever.answer_stream("支持什么上传？", top_k=3))
    full = "".join(deltas)
    assert "Markdown" in full or "上传" in full


def test_answer_stream_empty_query() -> None:
    _prepare_store()
    retriever = RAGRetriever()
    deltas = list(retriever.answer_stream("", top_k=3))
    assert len(deltas) >= 1
    assert "未在知识库中找到" in "".join(deltas)


def test_answer_stream_with_history() -> None:
    _prepare_store()
    retriever = RAGRetriever()
    history = [
        Message(role="user", content="你好"),
        Message(role="assistant", content="你好，请问有什么可以帮您？"),
    ]
    deltas = list(retriever.answer_stream("支持什么上传？", top_k=3, history=history))
    full = "".join(deltas)
    assert len(full) > 0


def test_retrieve_with_sources() -> None:
    _prepare_store()
    retriever = RAGRetriever()
    contexts, sources = retriever.retrieve_with_sources("上传", top_k=3)
    assert len(contexts) > 0
    assert len(sources) > 0
    assert sources[0].chunk_id


def test_no_context_stream() -> None:
    store = get_vector_store()
    store.clear()
    retriever = RAGRetriever()
    deltas = list(retriever.answer_stream("任意问题", top_k=3))
    assert "未在知识库中找到" in "".join(deltas)