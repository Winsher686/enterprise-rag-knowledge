"""RAG 检索服务：封装向量检索 + 生成，支持多轮、流式、多路召回。"""

import os
import time
from typing import Iterator, List, Optional

from app.core.logger import get_logger
from app.models.document import SearchResult
from app.models.qa import QAResponse, SourceRef
from app.models.session import Message
from app.services.llm import get_llm
from app.services.prompt import SYSTEM_PROMPT, build_user_prompt
from app.services.vectorstore import get_vector_store

logger = get_logger(__name__)

NO_ANSWER_TEXT = "未在知识库中找到相关依据，无法回答该问题。"


def _use_multi_retriever() -> bool:
    """是否启用多路召回。"""
    return os.getenv("USE_MULTI_RETRIEVER", "false").lower() == "true"


class RAGRetriever:
    """RAG 检索服务。"""

    def __init__(self) -> None:
        self.store = get_vector_store()
        self.llm = get_llm()

        # 多路召回（可选）
        self._multi = None
        if _use_multi_retriever():
            try:
                from app.services.retriever.multi_retriever import MultiRetriever
                self._multi = MultiRetriever()
                logger.info("启用多路召回")
            except Exception as exc:
                logger.warning("多路召回初始化失败，回退单路：%s", exc)

    def retrieve(self, query: str, top_k: int = 5) -> List[SearchResult]:
        if not query.strip():
            return []
        if self._multi is not None:
            return self._multi.search(query, top_k=top_k)
        return self.store.search(query, top_k=top_k)

    def answer(
        self,
        query: str,
        top_k: int = 5,
        temperature: float = 0.0,
        history: Optional[List[Message]] = None,
    ) -> QAResponse:
        start = time.perf_counter()

        if not query.strip():
            return QAResponse(query=query, answer=NO_ANSWER_TEXT, has_answer=False, sources=[])

        contexts = self.retrieve(query, top_k=top_k)
        if not contexts:
            elapsed = (time.perf_counter() - start) * 1000
            return QAResponse(
                query=query,
                answer=NO_ANSWER_TEXT,
                has_answer=False,
                sources=[],
                elapsed_ms=round(elapsed, 2),
            )

        user_prompt = build_user_prompt(query, contexts, history=history)
        try:
            answer = self.llm.chat(SYSTEM_PROMPT, user_prompt, temperature=temperature)
        except Exception as exc:
            logger.exception("LLM 调用失败")
            answer = f"LLM 调用失败：{exc}"

        has_answer = self._has_answer(answer)
        sources = self._build_sources(contexts) if has_answer else []

        elapsed = (time.perf_counter() - start) * 1000
        return QAResponse(
            query=query,
            answer=answer,
            has_answer=has_answer,
            sources=sources,
            elapsed_ms=round(elapsed, 2),
        )

    def answer_stream(
        self,
        query: str,
        top_k: int = 5,
        temperature: float = 0.0,
        history: Optional[List[Message]] = None,
    ) -> Iterator[str]:
        if not query.strip():
            yield NO_ANSWER_TEXT
            return

        contexts = self.retrieve(query, top_k=top_k)
        if not contexts:
            yield NO_ANSWER_TEXT
            return

        user_prompt = build_user_prompt(query, contexts, history=history)
        try:
            for delta in self.llm.chat_stream(SYSTEM_PROMPT, user_prompt, temperature=temperature):
                yield delta
        except Exception as exc:
            logger.exception("LLM 流式调用失败")
            yield f"LLM 调用失败：{exc}"

    def retrieve_with_sources(self, query: str, top_k: int = 5):
        contexts = self.retrieve(query, top_k=top_k)
        return contexts, self._build_sources(contexts)

    # ------------------------------------------------------------------
    @staticmethod
    def _has_answer(answer: str) -> bool:
        if not answer or not answer.strip():
            return False
        if NO_ANSWER_TEXT in answer:
            return False
        if "未在知识库中找到" in answer:
            return False
        return True

    @staticmethod
    def _build_sources(contexts: List[SearchResult]) -> List[SourceRef]:
        sources: List[SourceRef] = []
        for ctx in contexts:
            sources.append(SourceRef(
                chunk_id=ctx.chunk_id,
                doc_id=ctx.doc_id,
                title=ctx.title,
                score=ctx.score,
                snippet=ctx.content[:200],
                source=ctx.metadata.get("source", "") if ctx.metadata else "",
            ))
        return sources