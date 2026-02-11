"""
数据库 ORM 模型

表设计：
- sessions: 会话记录
- messages: 消息记录
- generation_tasks: 视频生成任务记录
"""
from datetime import datetime
from typing import Literal
from sqlalchemy import String, DateTime, ForeignKey, Text, Float, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .session import Base


class Session(Base):
    """
    会话记录

    代表一次用户交互会话，包含多个消息
    """
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    """会话 ID (UUID)"""

    title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    """会话标题（可选）"""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    """创建时间"""

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    """更新时间"""

    # 关系
    messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
    )
    """会话的消息列表"""

    tasks: Mapped[list["GenerationTask"]] = relationship(
        "GenerationTask",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="GenerationTask.created_at",
    )
    """会话的任务列表"""


class Message(Base):
    """
    消息记录

    存储用户和 AI 之间的对话消息
    """
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    """消息 ID (UUID)"""

    session_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    """所属会话 ID"""

    role: Mapped[Literal["user", "assistant", "system"]] = mapped_column(
        String(20), nullable=False, index=True
    )
    """角色类型"""

    content: Mapped[str] = mapped_column(Text, nullable=False)
    """消息内容"""

    extra_data: Mapped[dict | None] = mapped_column("extra_data", JSON, nullable=True)
    """额外元数据 (JSON 格式)"""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    """创建时间"""

    # 关系
    session: Mapped["Session"] = relationship("Session", back_populates="messages")


class GenerationTask(Base):
    """
    视频生成任务记录

    存储视频生成的任务信息和结果
    """
    __tablename__ = "generation_tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    """任务 ID (UUID)"""

    session_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("sessions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    """关联会话 ID (可选)"""

    # 输入参数
    topic: Mapped[str] = mapped_column(String(500), nullable=False)
    """视频主题"""

    style: Mapped[str] = mapped_column(String(50), nullable=False, default="minimal")
    """风格名称"""

    theme: Mapped[str | None] = mapped_column(String(100), nullable=True)
    """子主题"""

    # 任务状态
    status: Mapped[Literal["pending", "running", "completed", "failed"]] = mapped_column(
        String(20), nullable=False, default="pending", index=True
    )
    """任务状态"""

    step: Mapped[str | None] = mapped_column(String(50), nullable=True)
    """当前步骤"""

    progress: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    """进度 (0.0 - 1.0)"""

    # 输出结果
    final_video_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    """最终视频 URL"""

    scene_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    """场景数量"""

    # 场景数据 (JSON 存储)
    scenes: Mapped[list[dict] | None] = mapped_column(JSON, nullable=True)
    """场景数据列表"""

    # 错误信息
    errors: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    """错误信息列表"""

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    """创建时间"""

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    """更新时间"""

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    """完成时间"""

    # 关系
    session: Mapped["Session"] = relationship("Session", back_populates="tasks")
