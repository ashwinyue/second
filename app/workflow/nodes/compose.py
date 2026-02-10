"""
视频合成节点
"""
import logging
import uuid
import asyncio
from pathlib import Path

from ...state import AgentState
from ...config import get_settings

logger = logging.getLogger(__name__)


async def compose_node(state: AgentState) -> dict:
    """合成视频片段"""
    scenes = state.get("scenes", [])
    settings = get_settings()

    # 收集视频路径
    video_paths = []
    for scene in scenes:
        path = scene.get("video_url") or scene.get("image_url")
        if path:
            video_paths.append(Path(path))

    if not video_paths:
        return {
            "step": "failed",
            "errors": ["没有可用的视频片段"],
        }

    # 输出路径
    output_path = settings.output_dir / "composed" / f"{uuid.uuid4().hex}.mp4"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # FFmpeg 合成
    filter_complex = ""
    for i in range(len(video_paths)):
        filter_complex += f"[{i}:v]"
    filter_complex += f"concat=n={len(video_paths)}:v=1[outv]"

    cmd = [
        "ffmpeg",
        *[item for path in video_paths for item in ("-i", str(path))],
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "23",
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

    return {
        "composed_video_url": str(output_path),
        "step": "narrating",
    }
