"""
视频合成节点
"""
import logging
import uuid
import asyncio
import tempfile
from pathlib import Path

from ...state import AgentState
from ...config import get_settings

logger = logging.getLogger(__name__)


async def _download_to_temp(url: str) -> Path:
    """下载 MinIO 文件到临时目录"""
    import httpx

    async with httpx.AsyncClient(timeout=60.0) as client:
        r = await client.get(url)
        r.raise_for_status()

    # 创建临时文件
    suffix = Path(url).suffix or ".mp4"
    temp_file = Path(tempfile.gettempdir()) / f"{uuid.uuid4().hex}{suffix}"
    temp_file.write_bytes(r.content)
    return temp_file


async def compose_node(state: AgentState) -> dict:
    """合成视频片段"""
    scenes = state.get("scenes", [])

    # 收集视频 URL
    video_urls = []
    for scene in scenes:
        url = scene.get("video_url") or scene.get("image_url")
        if url:
            video_urls.append(url)

    if not video_urls:
        return {
            "step": "failed",
            "errors": ["没有可用的视频片段"],
        }

    # 下载所有视频到临时文件
    temp_paths = []
    try:
        for url in video_urls:
            temp_path = await _download_to_temp(url)
            temp_paths.append(temp_path)
            logger.info(f"下载视频到临时文件: {temp_path}")

        # 输出临时路径
        output_path = Path(tempfile.gettempdir()) / f"{uuid.uuid4().hex}.mp4"

        # FFmpeg 合成
        filter_complex = ""
        for i in range(len(temp_paths)):
            filter_complex += f"[{i}:v]"
        filter_complex += f"concat=n={len(temp_paths)}:v=1[outv]"

        cmd = [
            "ffmpeg",
            *[item for path in temp_paths for item in ("-i", str(path))],
            "-filter_complex", filter_complex,
            "-map", "[outv]",
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "23",
            "-movflags", "faststart",
            "-pix_fmt", "yuv420p",
            "-y",
            str(output_path),
        ]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise RuntimeError(f"FFmpeg 失败: {stderr.decode()}")

        logger.info(f"视频合成成功: {output_path}")

        # 上传到 MinIO
        from ...services.storage import get_storage_service
        storage = get_storage_service()

        minio_url = storage.upload_file(output_path, "video/mp4")
        logger.info(f"合成视频已上传到 MinIO: {minio_url}")

        return {
            "composed_video_url": minio_url,
            "step": "narrating",
        }

    finally:
        # 清理临时文件
        for temp_path in temp_paths:
            try:
                temp_path.unlink()
            except Exception:
                pass
