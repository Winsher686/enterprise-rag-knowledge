"""关键词检索测试。"""

from app.models.document import Chunk
from app.services.retriever.keyword_retriever import KeywordRetriever, jaccard, tokenize


def _make_chunk(cid: str, content: str) -> Chunk:
    return Chunk(
        chunk_id=cid,
        doc_id="doc-1",
        content=content,
        raw_content=content,
        title="测试",
        metadata={},
    )


def test_tokenize() -> None:
    tokens = tokenize("企业知识库支持 Markdown 上传")
    assert len(tokens) > 0
    assert "markdown" in tokens


def test_jaccard() -> None:
    assert jaccard([], []) == 0.0
    assert jaccard(["a"], ["a"]) == 1.0
    assert jaccard(["a", "b"], ["a", "c"]) > 0


def test_keyword_search() -> None:
    retriever = KeywordRetriever()
    retriever.add_chunks([
        _make_chunk("c1", "企业知识库支持 Markdown 上传"),
        _make_chunk("c2", "用户可以用自然语言提问"),
        _make_chunk("c3", "系统返回答案并附带引用来源"),
    ])
    results = retriever.search("Markdown 上传", top_k=2)
    assert len(results) > 0
    assert results[0].chunk_id == "c1"


def test_keyword_search_empty() -> None:
    retriever = KeywordRetriever()
    assert retriever.search("查询", top_k=5) == []


def test_keyword_clear() -> None:
    retriever = KeywordRetriever()
    retriever.add_chunks([_make_chunk("c1", "内容")])
    retriever.clear()
    assert retriever.search("内容", top_k=5) == []