"""HyDE 检索：LLM 生成假设答案，再检索。

原理：
    用户问题 → LLM 生成假设性文档 → 向量化 → 检索
因为假设文档更接近真实文档的语义分布，检索效果更好。
"""

from typing import List

from app.core.logger import get_logger
from app.models.document import SearchResult
from app.services.llm import get_llm
from app.services.vectorstore import get_vector_store

logger = get_logger(__name__)

_HYDE_PROMPT = """请针对下面的问题，写一段简洁的、假设性的答案文档，用于知识库检索。
不要解释，直接输出假设文档内容。

问题：{query}

假设文档："""


class HydeRetriever:
    """HyDE 检索器。"""

    def __init__(self, max_tokens: int = 300) -> None:
        self._llm = get_llm()
        self._store = get_vector_store()
        self._max_tokens = max_tokens

    def generate_hypothetical(self, query: str) -> str:
        """生成假设文档。"""
        if not query.strip():
            return ""
        prompt = _HYDE_PROMPT.format(query=query)
        try:
            doc = self._llm.chat(
                system_prompt="你是一个知识库检索助手。",
                user_prompt=prompt,
                temperature=0.3,
                max_tokens=self._max_tokens,
            )
            return doc.strip()
        except Exception as exc:
            logger.warning("HyDE 生成失败：%s", exc)
            return ""

    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        if not query.strip():
            return []

        hypothetical = self.generate_hypothetical(query)
        if not hypothetical:
            # 回退：直接用原 query
            return self._store.search(query, top_k=top_k)

        # 用"原问题 + 假设答案"组合检索
        combined = f"{query}\n{hypothetical}"
        return self._store.search(combined, top_k=top_k)