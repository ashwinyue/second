"""
API 请求/响应模型
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class GenerationRequest(BaseModel):
    """视频生成请求"""

    topic: str = Field(..., description="视频主题", min_length=1, max_length=200)
    philosopher: Optional[str] = Field(None, description="指定哲学家")
    science_type: Optional[str] = Field(None, description="关联科学类型")
    style_preset: str = Field(
        "dark_healing",
        description="风格预设",
        pattern="dark_healing|minimalist|vibrant|monochrome",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "topic": "自由意志是否存在",
                "philosopher": "萨特",
                "science_type": "神经科学",
                "style_preset": "dark_healing",
            }
        }


class SceneInfo(BaseModel):
    """场景信息"""

    id: int
    text: str
    type: str
    duration: float
    emotion: str
    image_url: Optional[str] = None
    video_url: Optional[str] = None


class TaskStatus(BaseModel):
    """任务状态"""

    task_id: str
    status: Literal["pending", "running", "completed", "failed"]
    step: str
    progress: float = Field(..., ge=0, le=1, description="进度 0-1")
    created_at: datetime
    updated_at: datetime
    scenes: Optional[list[SceneInfo]] = None
    final_video_url: Optional[str] = None
    errors: Optional[list[str]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "abc123",
                "status": "running",
                "step": "imaging",
                "progress": 0.4,
                "created_at": "2026-01-01T00:00:00Z",
                "updated_at": "2026-01-01T00:01:00Z",
            }
        }


class GenerationResponse(BaseModel):
    """生成响应"""

    task_id: str
    status: Literal["pending", "running", "completed", "failed"]
    message: str = "任务已创建"

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "abc123",
                "status": "pending",
                "message": "任务已创建，使用 WebSocket 获取实时进度",
            }
        }


class HealthResponse(BaseModel):
    """健康检查响应"""

    status: str = "healthy"
    version: str = "1.0.0"
    services: dict[str, bool]

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "services": {"llm": True, "image": True, "video": True, "tts": True},
            }
        }
