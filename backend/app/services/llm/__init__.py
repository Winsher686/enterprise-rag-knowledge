"""LLM 工厂。"""

from functools import lru_cache

from app.core.config import settings
from app.core.logger import get_logger
from app.services.llm.base import BaseLLM
from app.services.llm.mock_llm import MockLLM

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def get_llm() -> BaseLLM:
    """返回全局唯一的 LLM 实例。

    - LLM_PROVIDER=mock → MockLLM
    - LLM_PROVIDER=openai 或配置了 API Key → OpenAICompatLLM
    - 未配置 → MockLLM
    """
    import os

    provider = os.getenv("LLM_PROVIDER", "auto").lower()

    if provider == "mock":
        logger.info("使用 MockLLM（显式指定）")
        return MockLLM()

    if provider in ("openai", "qwen") and settings.LLM_API_KEY and settings.LLM_BASE_URL:
        from app.services.llm.openai_compat_llm import OpenAICompatLLM
        logger.info("使用 OpenAICompatLLM，model=%s", settings.LLM_MODEL)
        return OpenAICompatLLM(
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL,
            model=settings.LLM_MODEL,
        )

    if provider == "auto" and settings.LLM_API_KEY and settings.LLM_BASE_URL:
        try:
            from app.services.llm.openai_compat_llm import OpenAICompatLLM
            logger.info("使用 OpenAICompatLLM（auto），model=%s", settings.LLM_MODEL)
            return OpenAICompatLLM(
                api_key=settings.LLM_API_KEY,
                base_url=settings.LLM_BASE_URL,
                model=settings.LLM_MODEL,
            )
        except Exception as exc:
            logger.warning("OpenAI 兼容 LLM 不可用，降级为 MockLLM：%s", exc)

    logger.info("使用 MockLLM")
    return MockLLM()


__all__ = ["BaseLLM", "MockLLM", "get_llm"]