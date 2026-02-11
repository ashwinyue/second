# PostgreSQL 数据库集成

本文档说明如何使用项目的 PostgreSQL 数据库功能。

## 架构概览

### ORM 框架
- **SQLAlchemy 2.0** (async) - Python SQL 工具包和 ORM
- **asyncpg** - 高性能异步 PostgreSQL 驱动

### 表结构设计

#### `sessions` - 会话表
```sql
CREATE TABLE sessions (
    id VARCHAR(36) PRIMARY KEY,  -- UUID
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

#### `messages` - 消息表
```sql
CREATE TABLE messages (
    id VARCHAR(36) PRIMARY KEY,        -- UUID
    session_id VARCHAR(36) NOT NULL,   -- 外键 -> sessions
    role VARCHAR(20) NOT NULL,         -- 'user' | 'assistant' | 'system'
    content TEXT NOT NULL,
    metadata JSON,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);
```

#### `generation_tasks` - 视频生成任务表
```sql
CREATE TABLE generation_tasks (
    id VARCHAR(36) PRIMARY KEY,              -- UUID
    session_id VARCHAR(36),                  -- 外键 -> sessions (可为空)
    topic VARCHAR(500) NOT NULL,
    style VARCHAR(50) NOT NULL DEFAULT 'minimal',
    theme VARCHAR(100),
    status VARCHAR(20) NOT NULL DEFAULT 'pending',  -- 'pending' | 'running' | 'completed' | 'failed'
    step VARCHAR(50),
    progress FLOAT NOT NULL DEFAULT 0.0,
    final_video_url VARCHAR(1000),
    scene_count INTEGER NOT NULL DEFAULT 0,
    scenes JSON,
    errors JSON,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE SET NULL
);
```

## Docker 部署

### 启动服务

```bash
# 启动所有服务（包括 PostgreSQL）
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看数据库日志
docker-compose logs -f postgres
```

### 环境变量配置

在 `.env` 文件中配置数据库连接：

```bash
# Docker 部署时使用
DATABASE_URL=postgresql+asyncpg://dear:dear_password@postgres:5432/dear_agent
DATABASE_ECHO=false
```

### 本地开发连接

如果需要在本地连接到 Docker 中的数据库：

```bash
# 使用 psql 连接
docker exec -it dear-postgres psql -U dear -d dear_agent

# 或使用本地 psql
psql -h localhost -p 5432 -U dear -d dear_agent
```

## API 接口

### 会话管理

#### 创建会话
```bash
POST /api/v1/sessions
```

响应：
```json
{
  "id": "abc123...",
  "created_at": "2026-01-01T00:00:00Z",
  "updated_at": "2026-01-01T00:00:00Z",
  "messages": [],
  "tasks": []
}
```

#### 获取会话列表
```bash
GET /api/v1/sessions?limit=50&days=30
```

#### 获取会话详情
```bash
GET /api/v1/sessions/{session_id}
```

#### 删除会话
```bash
DELETE /api/v1/sessions/{session_id}
```

### 消息管理

#### 添加消息
```bash
POST /api/v1/sessions/{session_id}/messages
Content-Type: application/json

{
  "role": "user",
  "content": "生命的意义是什么？",
  "metadata": null
}
```

#### 获取会话消息
```bash
GET /api/v1/sessions/{session_id}/messages?limit=100
```

### 任务管理

#### 获取会话任务
```bash
GET /api/v1/sessions/{session_id}/tasks
```

## 代码示例

### 仓库层使用

```python
from app.db import get_session
from app.db.repository import SessionRepository, MessageRepository, TaskRepository

async def example_usage():
    async with get_session() as session:
        # 创建会话
        db_session = await SessionRepository.create(session, session_id)

        # 添加消息
        await MessageRepository.create(
            session,
            message_id=uuid.uuid4().hex,
            session_id=session_id,
            role="user",
            content="用户输入",
        )

        # 创建任务
        task = await TaskRepository.create(
            session,
            task_id=uuid.uuid4().hex,
            topic="主题",
            style="camus",
            session_id=session_id,
        )

        # 更新任务状态
        await TaskRepository.update_status(
            session, task.id, status="running", step="writing"
        )

        # 完成任务
        await TaskRepository.complete_task(
            session, task.id, final_video_url="http://..."
        )
```

### 在路由中使用（依赖注入）

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_session

@router.get("/some-endpoint")
async def some_endpoint(session: AsyncSession = Depends(get_session)):
    sessions = await SessionRepository.list_recent(session, limit=10)
    return {"sessions": sessions}
```

## 测试

### 运行数据库测试

```bash
# 确保数据库已启动
docker-compose up -d postgres

# 运行测试脚本
python test/test_db.py
```

### 手动初始化数据库

```bash
python -m app.db.init_db
```

## 数据库维护

### 备份数据

```bash
# 备份整个数据库
docker exec dear-postgres pg_dump -U dear dear_agent > backup.sql

# 恢复备份
docker exec -i dear-postgres psql -U dear dear_agent < backup.sql
```

### 查看表结构

```sql
\d sessions
\d messages
\d generation_tasks
```

### 常用查询

```sql
-- 统计会话数量
SELECT COUNT(*) FROM sessions;

-- 查看最近的任务
SELECT id, topic, style, status, progress, created_at
FROM generation_tasks
ORDER BY created_at DESC
LIMIT 10;

-- 查看会话的消息数量
SELECT s.id, COUNT(m.id) as message_count
FROM sessions s
LEFT JOIN messages m ON s.id = m.session_id
GROUP BY s.id;
```

## 故障排查

### 连接失败

```bash
# 检查数据库是否运行
docker-compose ps postgres

# 查看数据库日志
docker-compose logs postgres

# 测试连接
docker exec dear-postgres pg_isready -U dear
```

### 权限问题

确保 `.env` 文件中的数据库凭据与 `docker-compose.yml` 中的配置一致：

```yaml
# docker-compose.yml
environment:
  - POSTGRES_USER=dear
  - POSTGRES_PASSWORD=dear_password
  - POSTGRES_DB=dear_agent
```

```bash
# .env
DATABASE_URL=postgresql+asyncpg://dear:dear_password@postgres:5432/dear_agent
```

### 重新初始化数据库

```bash
# 删除数据库卷
docker-compose down -v

# 重新启动
docker-compose up -d

# 数据库会在应用启动时自动初始化
```
