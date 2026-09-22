"""检索接口。"""

from fastapi import APIRouter, HTTPException

from app.core.logger import get_logger
from app.models.document import SearchRequest, SearchResponse
from app.services.vectorstore import get_vector_store

logger = get_logger(__name__)

router = APIRouter(tags=["search"])


@router.post("/search", response_model=SearchResponse, summary="向量检索")
async def search(req: SearchRequest) -> SearchResponse:
    """按查询文本检索相关 chunk。"""
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="query 不能为空")

    store = get_vector_store()
    if store.count() == 0:
        return SearchResponse(
            code=0,
            message="向量库为空，请先上传文档",
            query=req.query,
            top_k=req.top_k,
            results=[],
        )

    try:
        results = store.search(req.query, top_k=req.top_k)
    except Exception as exc:
        logger.exception("检索失败")
        raise HTTPException(status_code=500, detail=f"检索失败：{exc}") from exc

    return SearchResponse(
        code=0,
        message="success",
        query=req.query,
        top_k=req.top_k,
        results=results,
    )