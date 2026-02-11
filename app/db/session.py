"""
数据库会话管理

使用 SQLAlchemy 2.0 async API
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase
from ..config import get_settings


class Base(DeclarativeBase):
    """ORM 基类"""

    pass


_engine: AsyncEngine | None = None
_async_session_maker: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """获取数据库引擎"""
    global _engine
    if _engine is None:
        settings = get_settings()
        from sqlalchemy.ext.asyncio import create_async_engine

        _engine = create_async_engine(
            settings.database_url,
            echo=settings.database_echo,
        )
    return _engine


def get_session_maker() -> async_sessionmaker[AsyncSession]:
    """获取会话工厂"""
    global _async_session_maker
    if _async_session_maker is None:
        _async_session_maker = async_sessionmaker(
            get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _async_session_maker


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话（依赖注入）

    用法：
    ```python
    @router.get("/sessions")
    async def list_sessions(session: AsyncSession = Depends(get_db_session)):
        ...
    ```
    """
    async_session_maker = get_session_maker()
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

# 保留别名以兼容现有代码
get_session = get_db_session


async def init_db() -> None:
    """
    初始化数据库表结构

    在应用启动时调用
    """
    from . import models  # noqa: F401 确保模型被导入

    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """
    关闭数据库连接

    在应用关闭时调用
    """
    global _engine, _async_session_maker

    if _engine:
        await _engine.dispose()
        _engine = None
        _async_session_maker = None
