"""多轮会话数据模型。"""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field

Role = Literal["user", "assistant", "system"]


class Message(BaseModel):
    """单条消息。"""

    role: Role = Field(description="角色")
    content: str = Field(description="内容")
    timestamp: float = Field(default=0.0, description="时间戳")


class Session(BaseModel):
    """会话。"""

    session_id: str = Field(description="会话 ID")
    messages: List[Message] = Field(default_factory=list, description="消息列表")
    created_at: float = Field(default=0.0)
    updated_at: float = Field(default=0.0)


class QAStreamRequest(BaseModel):
    """流式问答请求。"""

    query: str = Field(description="用户问题")
    session_id: Optional[str] = Field(default=None, description="会话 ID，不传则新建")
    top_k: int = Field(default=5, ge=1, le=50)
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)