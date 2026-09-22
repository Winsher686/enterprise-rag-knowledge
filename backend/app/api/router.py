"""API 路由聚合。"""

from fastapi import APIRouter

from app.api import health, query, search, upload

api_router = APIRouter(prefix="/api")
api_router.include_router(health.router)
api_router.include_router(upload.router)
api_router.include_router(search.router)
api_router.include_router(query.router)