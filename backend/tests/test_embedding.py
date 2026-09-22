"""Embedding 单元测试。"""

from app.services.embedding.mock_embedding import MockEmbedding


def test_mock_embedding_dim() -> None:
    emb = MockEmbedding(dim=64)
    assert emb.dim == 64
    vec = emb.embed_query("测试")
    assert len(vec) == 64


def test_mock_embedding_deterministic() -> None:
    emb = MockEmbedding(dim=32)
    v1 = emb.embed_query("相同文本")
    v2 = emb.embed_query("相同文本")
    assert v1 == v2


def test_mock_embedding_different_texts() -> None:
    emb = MockEmbedding(dim=32)
    v1 = emb.embed_query("文本A")
    v2 = emb.embed_query("文本B")
    assert v1 != v2


def test_mock_embedding_batch() -> None:
    emb = MockEmbedding(dim=16)
    vecs = emb.embed_documents(["a", "b", "c"])
    assert len(vecs) == 3
    assert all(len(v) == 16 for v in vecs)


def test_mock_embedding_normalized() -> None:
    emb = MockEmbedding(dim=32)
    v = emb.embed_query("归一化测试")
    norm = sum(x * x for x in v) ** 0.5
    assert abs(norm - 1.0) < 1e-6