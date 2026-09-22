"""多路检索编排测试。"""

from app.models.document import Chunk
from app.services.retriever.multi_retriever import MultiRetriever


def _make_chunk(cid: str, content: str) -> Chunk:
    return Chunk(
        chunk_id=cid,
        doc_id="doc-1",
        content=content,
        raw_content=content,
        title="测试文档",
        metadata={"source": "test.md"},
    )


def _prepare() -> MultiRetriever:
    r = MultiRetriever(enable_hyde=False, enable_rerank=False, enable_cutoff=False)
    r.clear()
    r.add_chunks([
        _make_chunk("c1", "企业知识库支持 Markdown 和 PDF 上传。"),
        _make_chunk("c2", "用户可以用自然语言提问。"),
        _make_chunk("c3", "系统返回答案并附带引用来源。"),
        _make_chunk("c4", "PDF 解析使用 MinerU 或 PyMuPDF。"),
    ])
    return r


def test_multi_retriever_search() -> None:
    r = _prepare()
    results = r.search("Markdown 上传", top_k=3)
    assert len(results) > 0
    # 至少有一条包含 Markdown 或 上传
    combined = " ".join(x.content for x in results)
    assert "Markdown" in combined or "上传" in combined


def test_multi_retriever_empty_query() -> None:
    r = _prepare()
    assert r.search("", top_k=3) == []


def test_multi_retriever_clear() -> None:
    r = _prepare()
    r.clear()
    assert r.search("Markdown", top_k=3) == []


def test_multi_retriever_with_cutoff() -> None:
    r = MultiRetriever(enable_hyde=False, enable_rerank=False, enable_cutoff=True)
    r.clear()
    r.add_chunks([
        _make_chunk("c1", "企业知识库支持 Markdown 上传。"),
        _make_chunk("c2", "用户可以用自然语言提问。"),
        _make_chunk("c3", "系统返回答案并附带引用来源。"),
    ])
    results = r.search("Markdown", top_k=5)
    assert len(results) >= 1