"""Mock Embedding：基于哈希的确定性伪向量。

特点：
- 不依赖任何模型，不需要 GPU
- 相同文本得到相同向量（确定性）
- 不同文本向量不同
- 维度可控
用于开发和 CI。
"""

import hashlib
import math
from typing import List

from app.services.embedding.base import BaseEmbedding


class MockEmbedding(BaseEmbedding):
    """基于 SHA-256 的确定性伪向量。"""

    def __init__(self, dim: int = 128) -> None:
        if dim <= 0:
            raise ValueError("dim 必须大于 0")
        self._dim = dim

    @property
    def dim(self) -> int:
        return self._dim

    @property
    def name(self) -> str:
        return f"mock-embedding-{self._dim}"

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._embed_one(t) for t in texts]

    def embed_query(self, text: str) -> List[float]:
        return self._embed_one(text)

    # ------------------------------------------------------------------
    # 内部方法
    # ------------------------------------------------------------------
    def _embed_one(self, text: str) -> List[float]:
        """把文本映射为固定维度的单位向量。"""
        vec = [0.0] * self._dim
        # 用多个盐值哈希，填满维度，避免分布不均
        for i in range(self._dim):
            salt = f"{i}:".encode("utf-8")
            h = hashlib.sha256(salt + text.encode("utf-8")).digest()
            # 取前 4 字节转 int，映射到 [-1, 1]
            num = int.from_bytes(h[:4], "big", signed=False)
            vec[i] = (num / 0xFFFFFFFF) * 2.0 - 1.0

        # 归一化
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]