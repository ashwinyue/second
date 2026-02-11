#!/usr/bin/env python3
"""
数据库功能测试脚本

测试会话、消息、任务的 CRUD 操作
"""
import asyncio
import uuid
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.session import init_db, get_session_maker, close_db
from app.db.repository import SessionRepository, MessageRepository, TaskRepository
from app.config import get_settings


async def test_database():
    """测试数据库功能"""
    settings = get_settings()

    print("=" * 50)
    print("数据库功能测试")
    print("=" * 50)
    print(f"数据库: {settings.database_url}\n")

    # 初始化数据库
    print("1. 初始化数据库...")
    await init_db()
    print("   ✅ 数据库初始化成功\n")

    # 获取会话工厂
    session_maker = get_session_maker()

    async with session_maker() as session:
        # 测试创建会话
        print("2. 测试创建会话...")
        session_id = uuid.uuid4().hex
        db_session = await SessionRepository.create(session, session_id)
        print(f"   ✅ 创建会话: {db_session.id}\n")

        # 测试添加消息
        print("3. 测试添加消息...")
        user_msg = await MessageRepository.create(
            session,
            message_id=uuid.uuid4().hex,
            session_id=session_id,
            role="user",
            content="生命的意义是什么？",
        )
        print(f"   ✅ 用户消息: {user_msg.content[:20]}...")

        assistant_msg = await MessageRepository.create(
            session,
            message_id=uuid.uuid4().hex,
            session_id=session_id,
            role="assistant",
            content="生命的意义是一个哲学问题...",
        )
        print(f"   ✅ 助手消息: {assistant_msg.content[:20]}...\n")

        # 测试创建任务
        print("4. 测试创建任务...")
        task_id = uuid.uuid4().hex
        task = await TaskRepository.create(
            session,
            task_id=task_id,
            topic="生命的意义",
            style="camus",
            theme="荒诞",
            session_id=session_id,
        )
        print(f"   ✅ 创建任务: {task.id}\n")

        # 测试更新任务状态
        print("5. 测试更新任务状态...")
        await TaskRepository.update_status(
            session, task_id, status="running", step="writing", progress=0.1
        )
        await TaskRepository.update_scenes(
            session,
            task_id,
            scenes=[
                {"id": 1, "text": "场景1", "type": "hook"},
                {"id": 2, "text": "场景2", "type": "theory"},
            ],
        )
        print("   ✅ 任务状态更新成功\n")

        # 测试完成任务
        print("6. 测试完成任务...")
        await TaskRepository.complete_task(
            session, task_id, final_video_url="http://example.com/video.mp4"
        )
        print("   ✅ 任务标记为完成\n")

        # 测试查询会话
        print("7. 测试查询会话...")
        fetched_session = await SessionRepository.get_by_id(session, session_id)
        if fetched_session:
            print(f"   ✅ 获取会话: {fetched_session.id}")
            print(f"      消息数: {len(fetched_session.messages)}")
            print(f"      任务数: {len(fetched_session.tasks)}")
            print(f"      任务状态: {fetched_session.tasks[0].status}")
        print()

        # 提交事务
        await session.commit()

    # 测试查询最近会话
    print("8. 测试查询最近会话...")
    async with session_maker() as session:
        recent_sessions = await SessionRepository.list_recent(session, limit=10)
        print(f"   ✅ 最近会话数: {len(recent_sessions)}\n")

    # 测试查询最近任务
    print("9. 测试查询最近任务...")
    async with session_maker() as session:
        recent_tasks = await TaskRepository.list_recent(session, limit=10)
        print(f"   ✅ 最近任务数: {len(recent_tasks)}")
        for t in recent_tasks:
            print(f"      - {t.topic}: {t.status} ({t.progress:.0%})")
    print()

    print("=" * 50)
    print("✅ 所有测试通过！")
    print("=" * 50)

    # 关闭数据库连接
    await close_db()


if __name__ == "__main__":
    asyncio.run(test_database())
