"""健康检查接口。"""

from fastapi import APIRouter

from app.core.config import settings
from app.core.logger import get_logger
from app.models.common import HealthResponse

logger = get_logger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse, summary="健康检查")
async def health() -> HealthResponse:
    """返回服务基本状态，用于探活和部署检查。"""
    logger.debug("health check called")
    return HealthResponse(
        status="ok",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment="dev" if settings.DEBUG else "prod",
    )
