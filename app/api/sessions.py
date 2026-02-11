"""
会话和消息管理 API

提供会话创建、查询、消息记录等接口
"""
import logging
import uuid
from typing import Literal
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.session import get_db_session
from ..db.repository import SessionRepository, MessageRepository, TaskRepository
from ..db.models import Session as DBSession, Message as DBMessage, GenerationTask as DBTask

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sessions", tags=["sessions"])


# ============================================================================
# 请求/响应模型
# ============================================================================


class MessageResponse(BaseModel):
    """消息响应"""
    id: str
    role: Literal["user", "assistant", "system"]
    content: str
    extra_data: dict | None = None
    created_at: str

    class Config:
        from_attributes = True


class TaskSummaryResponse(BaseModel):
    """任务摘要响应"""
    id: str
    topic: str
    style: str
    status: Literal["pending", "running", "completed", "failed"]
    progress: float
    final_video_url: str | None = None
    created_at: str
    completed_at: str | None = None

    class Config:
        from_attributes = True


class SessionResponse(BaseModel):
    """会话响应"""
    id: str
    title: str | None = None
    created_at: str
    updated_at: str
    messages: list[MessageResponse] = []
    tasks: list[TaskSummaryResponse] = []

    class Config:
        from_attributes = True


class SessionListResponse(BaseModel):
    """会话列表响应"""
    sessions: list[SessionResponse]
    total: int


class CreateSessionRequest(BaseModel):
    """创建会话请求"""
    title: str | None = Field(None, description="会话标题（可选）")


class UpdateSessionRequest(BaseModel):
    """更新会话请求"""
    title: str = Field(..., min_length=1, max_length=200, description="会话标题")


class AddMessageRequest(BaseModel):
    """添加消息请求"""
    role: Literal["user", "assistant", "system"]
    content: str = Field(..., min_length=1, max_length=10000)
    extra_data: dict | None = None


# ============================================================================
# API 端点
# ============================================================================


@router.post(
    "",
    response_model=SessionResponse,
    summary="创建新会话",
)
async def create_session(
    request: CreateSessionRequest,
    db_session: AsyncSession = Depends(get_db_session),
) -> SessionResponse:
    """
    创建新的对话会话

    返回会话信息，包括会话 ID
    """
    session_id = uuid.uuid4().hex
    db_session_obj = await SessionRepository.create(
        db_session,
        session_id,
        title=request.title,
    )

    logger.info(f"创建会话: session_id={session_id}, title={request.title}")

    return _to_session_response(db_session_obj)


@router.get(
    "",
    response_model=SessionListResponse,
    summary="获取会话列表",
)
async def list_sessions(
    limit: int = 50,
    days: int = 30,
    db_session: AsyncSession = Depends(get_db_session),
) -> SessionListResponse:
    """
    获取最近的会话列表

    - **limit**: 最大返回数量
    - **days**: 查询最近几天的会话
    """
    sessions = await SessionRepository.list_recent(db_session, limit=limit, days=days)

    return SessionListResponse(
        sessions=[_to_session_response(s) for s in sessions],
        total=len(sessions),
    )


@router.get(
    "/{session_id}",
    response_model=SessionResponse,
    summary="获取会话详情",
)
async def get_session(
    session_id: str,
    db_session: AsyncSession = Depends(get_db_session),
) -> SessionResponse:
    """
    获取会话详情，包括所有消息和任务
    """
    db_session_obj = await SessionRepository.get_by_id(db_session, session_id)

    if not db_session_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在",
        )

    return _to_session_response(db_session_obj)


@router.patch(
    "/{session_id}",
    response_model=SessionResponse,
    summary="更新会话",
)
async def update_session(
    session_id: str,
    request: UpdateSessionRequest,
    db_session: AsyncSession = Depends(get_db_session),
) -> SessionResponse:
    """
    更新会话信息（如标题）

    支持 partial update
    """
    # 检查会话是否存在
    db_session_obj = await SessionRepository.get_by_id(db_session, session_id)
    if not db_session_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在",
        )

    # 更新标题
    success = await SessionRepository.update_title(db_session, session_id, request.title)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新失败",
        )

    logger.info(f"更新会话标题: session_id={session_id}, title={request.title}")

    # 返回更新后的会话
    updated_session = await SessionRepository.get_by_id(db_session, session_id)
    return _to_session_response(updated_session)


@router.delete(
    "/{session_id}",
    summary="删除会话",
)
async def delete_session(
    session_id: str,
    db_session: AsyncSession = Depends(get_db_session),
) -> dict:
    """
    删除会话及其关联的消息和任务
    """
    success = await SessionRepository.delete(db_session, session_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在",
        )

    logger.info(f"删除会话: session_id={session_id}")

    return {"message": "会话已删除"}


@router.post(
    "/{session_id}/messages",
    response_model=MessageResponse,
    summary="添加消息",
)
async def add_message(
    session_id: str,
    request: AddMessageRequest,
    db_session: AsyncSession = Depends(get_db_session),
) -> MessageResponse:
    """
    向会话添加新消息

    自动更新会话时间戳
    """
    # 检查会话是否存在
    db_session_obj = await SessionRepository.get_by_id(db_session, session_id)
    if not db_session_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在",
        )

    # 创建消息
    message_id = uuid.uuid4().hex
    db_message = await MessageRepository.create(
        db_session,
        message_id=message_id,
        session_id=session_id,
        role=request.role,
        content=request.content,
        extra_data=request.extra_data,
    )

    # 更新会话时间戳
    await SessionRepository.update_timestamp(db_session, session_id)

    logger.info(f"添加消息: message_id={message_id}, session_id={session_id}, role={request.role}")

    return _to_message_response(db_message)


@router.get(
    "/{session_id}/messages",
    response_model=list[MessageResponse],
    summary="获取会话消息",
)
async def get_messages(
    session_id: str,
    limit: int | None = None,
    db_session: AsyncSession = Depends(get_db_session),
) -> list[MessageResponse]:
    """
    获取会话的消息列表

    - **limit**: 最大返回数量
    """
    # 检查会话是否存在
    db_session_obj = await SessionRepository.get_by_id(db_session, session_id)
    if not db_session_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在",
        )

    messages = await MessageRepository.list_by_session(db_session, session_id, limit=limit)

    return [_to_message_response(m) for m in messages]


@router.get(
    "/{session_id}/tasks",
    response_model=list[TaskSummaryResponse],
    summary="获取会话任务",
)
async def get_session_tasks(
    session_id: str,
    limit: int | None = None,
    db_session: AsyncSession = Depends(get_db_session),
) -> list[TaskSummaryResponse]:
    """
    获取会话的任务列表

    - **limit**: 最大返回数量
    """
    # 检查会话是否存在
    db_session_obj = await SessionRepository.get_by_id(db_session, session_id)
    if not db_session_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在",
        )

    tasks = await TaskRepository.list_by_session(db_session, session_id, limit=limit)

    return [_to_task_summary_response(t) for t in tasks]


# ============================================================================
# 辅助函数
# ============================================================================


def _to_session_response(db_session: DBSession) -> SessionResponse:
    """转换数据库会话对象为响应模型"""
    from sqlalchemy import inspect

    # 安全获取关联数据，避免 lazy loading 导致的 greenlet 错误
    insp = inspect(db_session)

    # 直接使用已加载的值，避免触发 lazy loading
    messages_list = []
    loaded_messages = insp.attrs.messages.loaded_value
    if loaded_messages is not None:
        # loaded_values 是列表或 instrumentation 中定义的默认值
        try:
            if hasattr(loaded_messages, '__iter__') and not isinstance(loaded_messages, str):
                messages_list = [_to_message_response(m) for m in loaded_messages]
        except Exception:
            pass

    # 直接使用已加载的值，避免触发 lazy loading
    tasks_list = []
    loaded_tasks = insp.attrs.tasks.loaded_value
    if loaded_tasks is not None:
        try:
            if hasattr(loaded_tasks, '__iter__') and not isinstance(loaded_tasks, str):
                tasks_list = [_to_task_summary_response(t) for t in loaded_tasks]
        except Exception:
            pass

    return SessionResponse(
        id=db_session.id,
        title=db_session.title,
        created_at=db_session.created_at.isoformat(),
        updated_at=db_session.updated_at.isoformat(),
        messages=messages_list,
        tasks=tasks_list,
    )


def _to_message_response(message: DBMessage) -> MessageResponse:
    """转换数据库消息对象为响应模型"""
    return MessageResponse(
        id=message.id,
        role=message.role,
        content=message.content,
        extra_data=message.extra_data,
        created_at=message.created_at.isoformat(),
    )


def _to_task_summary_response(task: DBTask) -> TaskSummaryResponse:
    """转换数据库任务对象为摘要响应模型"""
    return TaskSummaryResponse(
        id=task.id,
        topic=task.topic,
        style=task.style,
        status=task.status,
        progress=task.progress,
        final_video_url=task.final_video_url,
        created_at=task.created_at.isoformat(),
        completed_at=task.completed_at.isoformat() if task.completed_at else None,
    )
