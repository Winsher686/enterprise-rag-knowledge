"""RRF 融合测试。"""

from app.models.document import SearchResult
from app.services.retriever.rrf import rrf_fuse


def _make(cid: str, score: float = 1.0) -> SearchResult:
    return SearchResult(
        chunk_id=cid,
        doc_id="doc-1",
        content=f"内容 {cid}",
        title="测试",
        score=score,
        metadata={},
    )


def test_rrf_empty() -> None:
    assert rrf_fuse([]) == []


def test_rrf_single_list() -> None:
    results = [_make("c1"), _make("c2"), _make("c3")]
    fused = rrf_fuse([results])
    assert len(fused) == 3
    # 排名靠前的 RRF 分数更高
    assert fused[0].chunk_id == "c1"
    assert fused[1].chunk_id == "c2"


def test_rrf_two_lists_overlap() -> None:
    list_a = [_make("c1"), _make("c2"), _make("c3")]
    list_b = [_make("c2"), _make("c1"), _make("c4")]
    fused = rrf_fuse([list_a, list_b])
    ids = [r.chunk_id for r in fused]
    # c1 和 c2 在两边都靠前，应该排在前列
    assert ids[0] in ("c1", "c2")
    assert ids[1] in ("c1", "c2")


def test_rrf_weights() -> None:
    list_a = [_make("c1"), _make("c2")]
    list_b = [_make("c2"), _make("c1")]
    # 给 list_b 更高权重，c2 应排第一
    fused = rrf_fuse([list_a, list_b], weights=[0.1, 10.0])
    assert fused[0].chunk_id == "c2"


def test_rrf_k_parameter() -> None:
    list_a = [_make("c1")]
    fused_small_k = rrf_fuse([list_a], k=1)
    fused_large_k = rrf_fuse([list_a], k=100)
    # k 越大，分数越小
    assert fused_small_k[0].score > fused_large_k[0].score