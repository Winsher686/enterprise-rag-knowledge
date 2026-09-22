"""文档、chunk、检索结果数据模型。"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Document(BaseModel):
    """解析后的原始文档。"""

    doc_id: str = Field(description="文档唯一 ID")
    title: str = Field(description="文档标题")
    content: str = Field(description="文档纯文本内容")
    source: str = Field(description="来源文件名或路径")
    file_type: str = Field(description="文件类型：md / pdf / txt")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="附加元数据")


class Chunk(BaseModel):
    """切分后的文档块。"""

    chunk_id: str = Field(description="chunk 唯一 ID")
    doc_id: str = Field(description="所属文档 ID")
    content: str = Field(description="chunk 内容（含标题注入前缀）")
    raw_content: str = Field(description="chunk 原始内容（不含前缀）")
    title: str = Field(description="所属文档标题")
    parent_title: Optional[str] = Field(default=None, description="父级标题")
    part: int = Field(default=0, description="同标题下的分片序号")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="附加元数据")


class UploadResponse(BaseModel):
    """上传接口响应。"""

    code: int = Field(default=0)
    message: str = Field(default="success")
    doc_id: str = Field(description="文档 ID")
    title: str = Field(description="文档标题")
    file_type: str = Field(description="文件类型")
    chunk_count: int = Field(description="切分后 chunk 数量")
    indexed: bool = Field(default=False, description="是否已写入向量库")
    chunks: List[Chunk] = Field(default_factory=list, description="chunk 列表")


class SearchResult(BaseModel):
    """单条检索结果。"""

    chunk_id: str = Field(description="chunk ID")
    doc_id: str = Field(description="所属文档 ID")
    content: str = Field(description="chunk 内容")
    title: str = Field(description="来源标题")
    score: float = Field(description="相似度分数，越大越相关")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="附加元数据")


class SearchRequest(BaseModel):
    """检索请求。"""

    query: str = Field(description="查询文本")
    top_k: int = Field(default=5, ge=1, le=50, description="返回条数")


class SearchResponse(BaseModel):
    """检索响应。"""

    code: int = Field(default=0)
    message: str = Field(default="success")
    query: str = Field(description="原始查询")
    top_k: int = Field(description="返回条数")
    results: List[SearchResult] = Field(default_factory=list, description="检索结果")