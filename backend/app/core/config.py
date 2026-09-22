"""应用配置模块。

使用 pydantic-settings 从环境变量 / .env 文件读取配置。
所有配置项通过 Settings 类统一管理，避免散落在各处。
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """全局配置。"""

    # ===== 应用 =====
    APP_NAME: str = "enterprise-rag-knowledge"
    APP_VERSION: str = "0.1.0"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    DEBUG: bool = False

    # ===== LLM =====
    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = ""
    LLM_MODEL: str = "qwen3-32b"

    # ===== Embedding =====
    EMBEDDING_MODEL: str = "BAAI/bge-m3"
    EMBEDDING_DIM: int = 1024

    # ===== Vector Store =====
    VECTOR_STORE: str = "chroma"
    MILVUS_HOST: str = "milvus"
    MILVUS_PORT: int = 19530
    CHROMA_PERSIST_DIR: str = "./data/chroma"

    # ===== MongoDB =====
    MONGO_URI: str = "mongodb://mongo:27017"
    MONGO_DB: str = "enterprise_rag"

    # ===== MinIO =====
    MINIO_ENDPOINT: str = "minio:9000"
    MINIO_ACCESS_KEY: str = ""
    MINIO_SECRET_KEY: str = ""
    MINIO_BUCKET: str = "rag-images"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """返回全局唯一的 Settings 实例。"""
    return Settings()


settings = get_settings()
