"""
音频处理节点
"""
import logging
import uuid
import asyncio
from pathlib import Path

from ...state import AgentState
from ...config import get_settings

logger = logging.getLogger(__name__)


async def narrator_node(state: AgentState) -> dict:
    """TTS 生成配音"""
    scenes = state.get("scenes", [])
    composed_path = state.get("composed_video_url")

    if not composed_path:
        return {
            "step": "failed",
            "errors": ["没有已合成的视频"],
        }

    # 合并所有文案
    full_text = " ".join([s["text"] for s in scenes])

    from ...services import get_tts_service
    tts = get_tts_service()

    try:
        audio_path = await tts.synthesize(text=full_text)

        return {
            "audio_url": str(audio_path),
            "step": "adding_audio",
        }

    except Exception as e:
        logger.error(f"语音合成失败: {e}")
        return {
            "step": "failed",
            "errors": [f"语音合成失败: {str(e)}"],
        }


async def add_audio_node(state: AgentState) -> dict:
    """将配音混合到视频"""
    composed_path = state.get("composed_video_url")
    audio_url = state.get("audio_url")

    if not composed_path or not audio_url:
        return {
            "step": "failed",
            "errors": ["缺少视频或音频"],
        }

    settings = get_settings()
    output_path = settings.output_dir / "final" / f"{uuid.uuid4().hex}.mp4"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # FFmpeg 混合音频
    cmd = [
        "ffmpeg",
        "-i", str(composed_path),
        "-i", str(audio_url),
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
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

    logger.info(f"最终视频生成: {output_path}")

    return {
        "final_video_url": str(output_path),
        "step": "done",
    }
