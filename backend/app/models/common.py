"""通用响应模型。"""

from typing import Any, Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """健康检查响应。"""

    status: str = Field(default="ok", description="服务状态")
    app_name: str = Field(description="应用名称")
    version: str = Field(description="应用版本")
    environment: str = Field(default="dev", description="运行环境")


class ErrorResponse(BaseModel):
    """通用错误响应。"""

    code: int = Field(description="错误码")
    message: str = Field(description="错误信息")
    detail: Optional[Any] = Field(default=None, description="详细信息")


class BaseResponse(BaseModel):
    """通用基础响应。"""

    code: int = Field(default=0, description="业务状态码，0 表示成功")
    message: str = Field(default="success", description="提示信息")
    data: Optional[Any] = Field(default=None, description="业务数据")
