"""
数据仓库层

提供数据库操作的抽象接口
"""
from datetime import datetime, timedelta
from typing import Literal
from sqlalchemy import select, update, delete, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .models import Session, Message, GenerationTask


class SessionRepository:
    """会话仓库"""

    @staticmethod
    async def create(
        session: AsyncSession,
        session_id: str,
        title: str | None = None,
    ) -> Session:
        """
        创建新会话

        Args:
            session: 数据库会话
            session_id: 会话 ID
            title: 会话标题（可选）

        Returns:
            创建的会话对象
        """
        db_session = Session(id=session_id, title=title)
        session.add(db_session)
        await session.flush()
        await session.refresh(db_session)
        return db_session

    @staticmethod
    async def get_by_id(session: AsyncSession, session_id: str) -> Session | None:
        """
        根据 ID 获取会话

        Args:
            session: 数据库会话
            session_id: 会话 ID

        Returns:
            会话对象，不存在时返回 None
        """
        from sqlalchemy.orm import selectinload

        stmt = (
            select(Session)
            .where(Session.id == session_id)
            .options(selectinload(Session.messages))
            .options(selectinload(Session.tasks))
        )
        result = await session.execute(stmt)
        db_session = result.scalar_one_or_none()

        # 手动排序关联的消息和任务
        if db_session:
            db_session.messages.sort(key=lambda m: m.created_at)
            db_session.tasks.sort(key=lambda t: t.created_at, reverse=True)

        return db_session

    @staticmethod
    async def list_recent(
        session: AsyncSession,
        limit: int = 50,
        days: int = 30,
    ) -> list[Session]:
        """
        获取最近的会话列表

        Args:
            session: 数据库会话
            limit: 最大返回数量
            days: 查询最近几天的会话

        Returns:
            会话列表
        """
        from sqlalchemy.orm import selectinload

        since = datetime.now() - timedelta(days=days)
        stmt = (
            select(Session)
            .where(Session.updated_at >= since)
            .order_by(Session.updated_at.desc())
            .limit(limit)
            .options(selectinload(Session.messages))
            .options(selectinload(Session.tasks))
        )
        result = await session.execute(stmt)
        sessions = result.scalars().all()

        # 手动排序关联的消息和任务
        for s in sessions:
            s.messages.sort(key=lambda m: m.created_at)
            s.tasks.sort(key=lambda t: t.created_at, reverse=True)

        return list(sessions)

    @staticmethod
    async def delete(session: AsyncSession, session_id: str) -> bool:
        """
        删除会话（级联删除关联的消息和任务）

        Args:
            session: 数据库会话
            session_id: 会话 ID

        Returns:
            是否删除成功
        """
        stmt = delete(Session).where(Session.id == session_id)
        result = await session.execute(stmt)
        return result.rowcount > 0

    @staticmethod
    async def update_timestamp(session: AsyncSession, session_id: str) -> None:
        """
        更新会话时间戳

        Args:
            session: 数据库会话
            session_id: 会话 ID
        """
        stmt = (
            update(Session)
            .where(Session.id == session_id)
            .values(updated_at=func.now())
        )
        await session.execute(stmt)

    @staticmethod
    async def update_title(session: AsyncSession, session_id: str, title: str) -> bool:
        """
        更新会话标题

        Args:
            session: 数据库会话
            session_id: 会话 ID
            title: 新标题

        Returns:
            是否更新成功
        """
        stmt = (
            update(Session)
            .where(Session.id == session_id)
            .values(title=title)
        )
        result = await session.execute(stmt)
        return result.rowcount > 0


class MessageRepository:
    """消息仓库"""

    @staticmethod
    async def create(
        session: AsyncSession,
        message_id: str,
        session_id: str,
        role: Literal["user", "assistant", "system"],
        content: str,
        extra_data: dict | None = None,
    ) -> Message:
        """
        创建新消息

        Args:
            session: 数据库会话
            message_id: 消息 ID
            session_id: 会话 ID
            role: 角色类型
            content: 消息内容
            extra_data: 额外元数据

        Returns:
            创建的消息对象
        """
        message = Message(
            id=message_id,
            session_id=session_id,
            role=role,
            content=content,
            extra_data=extra_data,
        )
        session.add(message)
        await session.flush()
        await session.refresh(message)
        return message

    @staticmethod
    async def list_by_session(
        session: AsyncSession,
        session_id: str,
        limit: int | None = None,
    ) -> list[Message]:
        """
        获取会话的消息列表

        Args:
            session: 数据库会话
            session_id: 会话 ID
            limit: 最大返回数量

        Returns:
            消息列表（按时间正序）
        """
        stmt = (
            select(Message)
            .where(Message.session_id == session_id)
            .order_by(Message.created_at)
        )
        if limit:
            stmt = stmt.limit(limit)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def delete_by_session(session: AsyncSession, session_id: str) -> int:
        """
        删除会话的所有消息

        Args:
            session: 数据库会话
            session_id: 会话 ID

        Returns:
            删除的消息数量
        """
        stmt = delete(Message).where(Message.session_id == session_id)
        result = await session.execute(stmt)
        return result.rowcount


class TaskRepository:
    """任务仓库"""

    @staticmethod
    async def create(
        session: AsyncSession,
        task_id: str,
        topic: str,
        style: str = "minimal",
        theme: str | None = None,
        session_id: str | None = None,
    ) -> GenerationTask:
        """
        创建新任务

        Args:
            session: 数据库会话
            task_id: 任务 ID
            topic: 视频主题
            style: 风格名称
            theme: 子主题
            session_id: 关联会话 ID

        Returns:
            创建的任务对象
        """
        task = GenerationTask(
            id=task_id,
            session_id=session_id,
            topic=topic,
            style=style,
            theme=theme,
            status="pending",
        )
        session.add(task)
        await session.flush()
        await session.refresh(task)
        return task

    @staticmethod
    async def get_by_id(session: AsyncSession, task_id: str) -> GenerationTask | None:
        """
        根据 ID 获取任务

        Args:
            session: 数据库会话
            task_id: 任务 ID

        Returns:
            任务对象，不存在时返回 None
        """
        stmt = select(GenerationTask).where(GenerationTask.id == task_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def update_status(
        session: AsyncSession,
        task_id: str,
        status: Literal["pending", "running", "completed", "failed"],
        step: str | None = None,
        progress: float | None = None,
    ) -> bool:
        """
        更新任务状态

        Args:
            session: 数据库会话
            task_id: 任务 ID
            status: 新状态
            step: 当前步骤
            progress: 进度值

        Returns:
            是否更新成功
        """
        values: dict = {"status": status}
        if step is not None:
            values["step"] = step
        if progress is not None:
            values["progress"] = progress

        if status == "completed":
            values["completed_at"] = func.now()

        stmt = update(GenerationTask).where(GenerationTask.id == task_id).values(**values)
        result = await session.execute(stmt)
        return result.rowcount > 0

    @staticmethod
    async def update_scenes(
        session: AsyncSession,
        task_id: str,
        scenes: list[dict],
    ) -> bool:
        """
        更新任务场景数据

        Args:
            session: 数据库会话
            task_id: 任务 ID
            scenes: 场景数据列表

        Returns:
            是否更新成功
        """
        stmt = (
            update(GenerationTask)
            .where(GenerationTask.id == task_id)
            .values(scenes=scenes, scene_count=len(scenes))
        )
        result = await session.execute(stmt)
        return result.rowcount > 0

    @staticmethod
    async def complete_task(
        session: AsyncSession,
        task_id: str,
        final_video_url: str,
    ) -> bool:
        """
        标记任务完成

        Args:
            session: 数据库会话
            task_id: 任务 ID
            final_video_url: 最终视频 URL

        Returns:
            是否更新成功
        """
        stmt = (
            update(GenerationTask)
            .where(GenerationTask.id == task_id)
            .values(
                status="completed",
                progress=1.0,
                final_video_url=final_video_url,
                completed_at=func.now(),
            )
        )
        result = await session.execute(stmt)
        return result.rowcount > 0

    @staticmethod
    async def fail_task(
        session: AsyncSession,
        task_id: str,
        errors: list[str],
    ) -> bool:
        """
        标记任务失败

        Args:
            session: 数据库会话
            task_id: 任务 ID
            errors: 错误信息列表

        Returns:
            是否更新成功
        """
        stmt = (
            update(GenerationTask)
            .where(GenerationTask.id == task_id)
            .values(status="failed", errors=errors, completed_at=func.now())
        )
        result = await session.execute(stmt)
        return result.rowcount > 0

    @staticmethod
    async def list_recent(
        session: AsyncSession,
        limit: int = 50,
        status: Literal["pending", "running", "completed", "failed"] | None = None,
    ) -> list[GenerationTask]:
        """
        获取最近的任务列表

        Args:
            session: 数据库会话
            limit: 最大返回数量
            status: 状态过滤

        Returns:
            任务列表
        """
        stmt = select(GenerationTask).order_by(GenerationTask.created_at.desc()).limit(limit)
        if status:
            stmt = stmt.where(GenerationTask.status == status)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def list_by_session(
        session: AsyncSession,
        session_id: str,
        limit: int | None = None,
    ) -> list[GenerationTask]:
        """
        获取会话的任务列表

        Args:
            session: 数据库会话
            session_id: 会话 ID
            limit: 最大返回数量

        Returns:
            任务列表
        """
        stmt = (
            select(GenerationTask)
            .where(GenerationTask.session_id == session_id)
            .order_by(GenerationTask.created_at.desc())
        )
        if limit:
            stmt = stmt.limit(limit)
        result = await session.execute(stmt)
        return list(result.scalars().all())
