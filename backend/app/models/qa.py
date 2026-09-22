"""RAG 问答相关数据模型。"""

from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.document import SearchResult


class SourceRef(BaseModel):
    """答案引用的来源。"""

    chunk_id: str = Field(description="chunk ID")
    doc_id: str = Field(description="文档 ID")
    title: str = Field(description="来源标题")
    score: float = Field(description="相似度分数")
    snippet: str = Field(description="原文片段")
    source: str = Field(default="", description="来源文件名")


class QARequest(BaseModel):
    """RAG 问答请求。"""

    query: str = Field(description="用户问题")
    top_k: int = Field(default=5, ge=1, le=50, description="检索条数")
    temperature: float = Field(default=0.0, ge=0.0, le=2.0, description="生成温度")


class QAResponse(BaseModel):
    """RAG 问答响应。"""

    code: int = Field(default=0)
    message: str = Field(default="success")
    query: str = Field(description="原始问题")
    answer: str = Field(description="模型答案")
    has_answer: bool = Field(description="是否有依据回答")
    sources: List[SourceRef] = Field(default_factory=list, description="引用来源")
    elapsed_ms: float = Field(default=0.0, description="耗时（毫秒）")