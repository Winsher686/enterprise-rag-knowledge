"""RAGRetriever 单元测试。"""

from app.models.document import Chunk
from app.services.retriever.rag_retriever import NO_ANSWER_TEXT, RAGRetriever
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


def test_rag_answer_with_context() -> None:
    _prepare_store()
    retriever = RAGRetriever()
    resp = retriever.answer("支持什么上传？", top_k=3)
    assert resp.has_answer is True
    assert len(resp.sources) > 0
    assert resp.elapsed_ms >= 0


def test_rag_answer_empty_query() -> None:
    _prepare_store()
    retriever = RAGRetriever()
    resp = retriever.answer("", top_k=3)
    assert resp.has_answer is False
    assert resp.answer == NO_ANSWER_TEXT


def test_rag_answer_empty_store() -> None:
    store = get_vector_store()
    store.clear()
    retriever = RAGRetriever()
    resp = retriever.answer("任意问题", top_k=3)
    assert resp.has_answer is False
    assert resp.sources == []