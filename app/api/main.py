"""
FastAPI 应用工厂
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .routes import router
from ..config import get_settings

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动
    settings = get_settings()

    # 创建输出目录
    settings.output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("应用启动成功")
    yield

    # 关闭
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

    # 静态文件服务 - 用于访问生成的视频和图片
    outputs_path = settings.output_dir
    if outputs_path.exists():
        app.mount("/outputs", StaticFiles(directory=str(outputs_path)), name="outputs")
        logger.info(f"静态文件服务已挂载: /outputs -> {outputs_path}")

    return app
