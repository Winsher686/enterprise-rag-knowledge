"""BGE-M3 Embedding 适配器（占位）。

真实使用时需要：
    pip install FlagEmbedding
并下载 BAAI/bge-m3 模型。
未安装时抛出友好错误。
"""

from typing import List

from app.services.embedding.base import BaseEmbedding


class BGEM3Embedding(BaseEmbedding):
    """BGE-M3 向量化适配器。"""

    def __init__(self, model_name: str = "BAAI/bge-m3", dim: int = 1024) -> None:
        try:
            from FlagEmbedding import BGEM3FlagModel  # noqa: F401
        except ImportError as exc:
            raise ImportError(
                "使用 BGE-M3 需要安装 FlagEmbedding：pip install FlagEmbedding"
            ) from exc

        self._model_name = model_name
        self._dim = dim
        self._model = BGEM3FlagModel(model_name, use_fp16=True)

    @property
    def dim(self) -> int:
        return self._dim

    @property
    def name(self) -> str:
        return self._model_name

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        output = self._model.encode(texts, batch_size=16, max_length=512)
        return [list(map(float, v)) for v in output["dense_vecs"]]

    def embed_query(self, text: str) -> List[float]:
        output = self._model.encode([text], max_length=512)
        return list(map(float, output["dense_vecs"][0]))