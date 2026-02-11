"""
API 请求/响应模型
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class GenerationRequest(BaseModel):
    """视频生成请求"""

    topic: str = Field(..., description="视频主题", min_length=1, max_length=200)

    # 风格配置
    style: Literal["camus", "healing", "knowledge", "humor", "growth", "minimal"] = Field(
        "minimal",
        description="风格名称: camus(加缪荒诞哲学), healing(温暖治愈), knowledge(硬核科普), humor(幽默搞笑), growth(成长觉醒), minimal(极简金句)",
    )
    theme: Optional[str] = Field(
        None,
        description="可选的子主题（用于某些风格的细分）",
    )

    # 向后兼容的旧参数（会映射到新的 style 参数）
    philosopher: Optional[str] = Field(
        None,
        description="[向后兼容] 指定哲学家（映射到camus风格）",
    )
    science_type: Optional[str] = Field(
        None,
        description="[向后兼容] 关联科学类型",
    )
    style_preset: Optional[str] = Field(
        None,
        description="[向后兼容] 旧风格预设（建议使用style参数）",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "topic": "生命的意义是什么",
                "style": "camus",
                "theme": "荒诞",
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
                "message": "任务已创建，使用 SSE 获取实时进度",
            }
        }


class HealthResponse(BaseModel):
    """健康检查响应"""

    status: str = "healthy"
    version: str = "2.0.0"  # 更新版本号
    services: dict[str, bool]

    # 新增：可用风格列表
    available_styles: dict[str, str] = Field(
        default={
            "camus": "加缪荒诞哲学 - 深度拷问、诗意克制",
            "healing": "温暖治愈 - 亲切陪伴、温柔鼓励",
            "knowledge": "硬核科普 - 权威数据、逻辑清晰",
            "humor": "幽默搞笑 - 反转套路、轻松调侃",
            "growth": "成长觉醒 - 认知升级、行动导向",
            "minimal": "极简金句 - 短小精悍、直击人心",
        },
        description="可用的风格列表",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "2.0.0",
                "services": {"llm": True, "image": True, "video": True, "tts": True},
                "available_styles": {
                    "camus": "加缪荒诞哲学",
                    "healing": "温暖治愈",
                    "knowledge": "硬核科普",
                    "humor": "幽默搞笑",
                    "growth": "成长觉醒",
                    "minimal": "极简金句",
                },
            }
        }
