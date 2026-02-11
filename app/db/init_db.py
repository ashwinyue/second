#!/usr/bin/env python3
"""
数据库初始化脚本

用于创建数据库表结构

用法:
    python -m app.db.init_db
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.db.session import init_db, get_engine
from app.config import get_settings


async def main():
    """初始化数据库表"""
    settings = get_settings()

    print(f"正在连接数据库: {settings.database_url}")

    try:
        await init_db()
        print("✅ 数据库表创建成功！")
        print("\n已创建以下表:")
        print("  - sessions: 会话记录")
        print("  - messages: 消息记录")
        print("  - generation_tasks: 视频生成任务记录")
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        sys.exit(1)
    finally:
        from app.db.session import get_engine
        engine = get_engine()
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
