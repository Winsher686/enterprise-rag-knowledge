"""FastAPI 应用入口。"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期钩子。"""
    logger.info("=" * 60)
    logger.info("%s v%s 启动中...", settings.APP_NAME, settings.APP_VERSION)
    logger.info("运行环境：%s", "DEBUG" if settings.DEBUG else "PROD")
    logger.info("监听地址：%s:%s", settings.APP_HOST, settings.APP_PORT)
    logger.info("=" * 60)
    yield
    logger.info("%s 已关闭", settings.APP_NAME)


def create_app() -> FastAPI:
    """创建 FastAPI 实例。"""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="企业知识智能问答平台 - 后端服务",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)

    return app


app = create_app()
