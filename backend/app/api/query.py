"""RAG 问答接口（同步 + 流式）。"""

import json
from typing import AsyncIterator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.core.logger import get_logger
from app.models.qa import QARequest, QAResponse
from app.models.session import Message, QAStreamRequest
from app.services.retriever import RAGRetriever
from app.services.session import get_session_store

logger = get_logger(__name__)

router = APIRouter(tags=["query"])


@router.post("/query", response_model=QAResponse, summary="RAG 问答（同步）")
async def query(req: QARequest) -> QAResponse:
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="query 不能为空")
    try:
        retriever = RAGRetriever()
        return retriever.answer(
            query=req.query,
            top_k=req.top_k,
            temperature=req.temperature,
        )
    except Exception as exc:
        logger.exception("RAG 问答失败")
        raise HTTPException(status_code=500, detail=f"问答失败：{exc}") from exc


def _sse_event(event: str, data: dict) -> str:
    """构造 SSE 事件。"""
    payload = json.dumps(data, ensure_ascii=False)
    return f"event: {event}\ndata: {payload}\n\n"


@router.post("/query/stream", summary="RAG 问答（SSE 流式）")
async def query_stream(req: QAStreamRequest):
    """SSE 流式问答。

    事件类型：
    - ready：会话已就绪，返回 session_id
    - delta：答案增量
    - sources：引用来源
    - final：结束，返回完整答案
    - error：错误
    """
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="query 不能为空")

    async def event_generator() -> AsyncIterator[str]:
        session_store = get_session_store()
        session = session_store.get_or_create(req.session_id)
        session_id = session.session_id

        try:
            yield _sse_event("ready", {"session_id": session_id})

            history = session_store.get_history(session_id, limit=10)

            # 先记录用户消息
            session_store.append(session_id, Message(role="user", content=req.query))

            retriever = RAGRetriever()
            contexts, sources = retriever.retrieve_with_sources(req.query, top_k=req.top_k)

            full_answer = ""
            if not contexts:
                full_answer = "未在知识库中找到相关依据，无法回答该问题。"
                yield _sse_event("delta", {"text": full_answer})
            else:
                for delta in retriever.answer_stream(
                    req.query,
                    top_k=req.top_k,
                    temperature=req.temperature,
                    history=history,
                ):
                    full_answer += delta
                    yield _sse_event("delta", {"text": delta})

            # 推送来源
            yield _sse_event("sources", {
                "sources": [s.model_dump() for s in sources],
            })

            # 记录助手消息
            session_store.append(session_id, Message(role="assistant", content=full_answer))

            yield _sse_event("final", {
                "session_id": session_id,
                "answer": full_answer,
                "has_answer": bool(contexts),
            })

        except Exception as exc:
            logger.exception("流式问答失败")
            yield _sse_event("error", {"message": str(exc)})

    return StreamingResponse(event_generator(), media_type="text/event-stream")