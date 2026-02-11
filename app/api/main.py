"""
FastAPI 应用工厂
"""
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .routes import router
from .sessions import router as sessions_router
from ..config import get_settings


# 简单的测试端点
from fastapi import APIRouter

test_router = APIRouter(prefix="/test", tags=["test"])

@test_router.get("/sessions")
async def test_sessions():
    """测试会话列表"""
    try:
        from ..db import get_engine, get_session_maker
        from ..db.models import Session as DBSession
        from sqlalchemy import select, text

        # 测试原始查询
        engine = get_engine()
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT COUNT(*) FROM sessions"))
            count = result.scalar()

        # 测试 ORM 查询
        async_session_maker = get_session_maker()
        async with async_session_maker() as session:
            stmt = select(DBSession).limit(1)
            result = await session.execute(stmt)
            sessions = result.scalars().all()

        return {"status": "ok", "count": count}
    except Exception as e:
        import traceback
        return {"status": "error", "message": str(e), "trace": traceback.format_exc()[:500]}

# 配置日志
def setup_logging():
    """配置日志系统"""
    settings = get_settings()
    log_dir = settings.output_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    # 日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # 文件处理器（轮转，每个文件最大 10MB，保留 5 个备份）
    file_handler = RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    return logging.getLogger(__name__)


logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动
    settings = get_settings()

    # 创建输出目录
    settings.output_dir.mkdir(parents=True, exist_ok=True)

    # 初始化数据库
    from ..db import init_db
    try:
        await init_db()
        logger.info("数据库初始化成功")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise

    logger.info("应用启动成功")
    yield

    # 关闭
    from ..db import close_db
    await close_db()
    logger.info("应用关闭")


def create_app() -> FastAPI:
    """创建 FastAPI 应用"""
    settings = get_settings()

    app = FastAPI(
        title="DEAR Agent API",
        description="Digital Enlightenment & Artistic Reasoning - 哲学科普视频生成 Agent (SSE 流式返回)",
        version="2.0.0",
        lifespan=lifespan,
    )

    # CORS 配置
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 生产环境应限制具体域名
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册路由
    app.include_router(router, prefix="/api/v1")
    app.include_router(sessions_router, prefix="/api/v1")
    app.include_router(test_router, prefix="/api/v1")

    # 静态文件服务 - 用于访问生成的视频和图片
    outputs_path = settings.output_dir
    if outputs_path.exists():
        app.mount("/outputs", StaticFiles(directory=str(outputs_path)), name="outputs")
        logger.info(f"静态文件服务已挂载: /outputs -> {outputs_path}")

    return app


# 创建 app 实例供 uvicorn 直接导入
app = create_app()
