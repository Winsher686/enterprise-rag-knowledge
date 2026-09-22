"""断崖检测截断测试。"""

from app.models.document import SearchResult
from app.services.reranker.cutoff import cliff_cutoff


def _make(cid: str, score: float) -> SearchResult:
    return SearchResult(
        chunk_id=cid,
        doc_id="doc-1",
        content=f"内容 {cid}",
        title="测试",
        score=score,
        metadata={},
    )


def test_cutoff_empty() -> None:
    assert cliff_cutoff([]) == []


def test_cutoff_below_min_keep() -> None:
    results = [_make("c1", 0.9), _make("c2", 0.8)]
    out = cliff_cutoff(results, min_keep=3)
    assert len(out) == 2


def test_cutoff_cliff_detected() -> None:
    results = [
        _make("c1", 0.95),
        _make("c2", 0.93),
        _make("c3", 0.89),
        _make("c4", 0.87),
        _make("c5", 0.82),
        _make("c6", 0.30),  # 断崖
        _make("c7", 0.28),
    ]
    out = cliff_cutoff(results, abs_threshold=0.5, rel_threshold=0.25)
    # 应该在 c6 之前截断，保留 5 条
    assert len(out) == 5
    assert out[-1].chunk_id == "c5"


def test_cutoff_max_keep() -> None:
    results = [_make(f"c{i}", 1.0 - i * 0.001) for i in range(20)]
    out = cliff_cutoff(results, max_keep=5)
    assert len(out) == 5


def test_cutoff_no_cliff() -> None:
    results = [_make(f"c{i}", 1.0 - i * 0.01) for i in range(5)]
    out = cliff_cutoff(results, abs_threshold=0.5, rel_threshold=0.25)
    # 差距都很小，不应截断
    assert len(out) == 5