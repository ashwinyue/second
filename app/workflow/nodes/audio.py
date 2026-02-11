"""
音频处理节点
"""
import logging
import uuid
import asyncio
import json
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


async def get_media_duration(file_path: str) -> float:
    """获取媒体文件时长（秒）"""
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "json",
        str(file_path),
    ]

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await process.communicate()
    result = json.loads(stdout.decode())
    return float(result["format"]["duration"])


async def narrator_node(state: AgentState) -> dict:
    """TTS 生成配音"""
    scenes = state.get("scenes", [])
    composed_url = state.get("composed_video_url")

    if not composed_url:
        return {
            "step": "failed",
            "errors": ["没有已合成的视频"],
        }

    # 合并所有文案
    full_text = " ".join([s["text"] for s in scenes])

    from ...services import get_tts_service
    tts = get_tts_service()

    try:
        audio_url = await tts.synthesize(text=full_text)

        return {
            "audio_url": audio_url,
            "step": "adding_audio",
        }

    except Exception as e:
        logger.error(f"语音合成失败: {e}")
        # Fallback: 直接使用合成视频作为最终视频
        logger.info(f"TTS服务不可用，使用无音频视频作为最终输出: {composed_url}")
        return {
            "final_video_url": composed_url,  # 直接使用合成视频
            "audio_url": "",  # 清空音频URL，触发直接完成
            "step": "done",  # 跳过add_audio步骤
        }


async def add_audio_node(state: AgentState) -> dict:
    """将配音混合到视频，自动适配时长，并添加背景音乐"""
    composed_url = state.get("composed_video_url")
    audio_url = state.get("audio_url")

    if not composed_url or not audio_url:
        return {
            "step": "failed",
            "errors": ["缺少视频或音频"],
        }

    settings = get_settings()

    # 获取背景音乐路径和配置
    bgm_path = _get_background_music() if settings.bgm_enabled else None
    use_bgm = bgm_path and Path(bgm_path).exists()

    if use_bgm:
        logger.info(f"使用背景音乐: {bgm_path}, 音量: {settings.bgm_volume}")

    # 下载 MinIO 文件到临时目录
    temp_video_path = None
    temp_audio_path = None
    output_path = None

    try:
        temp_video_path = await _download_to_temp(composed_url)
        temp_audio_path = await _download_to_temp(audio_url)
        output_path = Path(tempfile.gettempdir()) / f"{uuid.uuid4().hex}.mp4"

        # 获取视频和音频时长
        video_duration = await get_media_duration(temp_video_path)
        audio_duration = await get_media_duration(temp_audio_path)

        logger.info(f"视频时长: {video_duration:.2f}秒, 音频时长: {audio_duration:.2f}秒")

        # 构建 FFmpeg 命令
        cmd = [
            "ffmpeg",
            "-i", str(temp_video_path),  # 0:v 视频
            "-i", str(temp_audio_path),      # 1:a 人声
        ]

        # 添加背景音乐输入
        if use_bgm:
            cmd.extend(["-i", str(bgm_path)])  # 2:a 背景音乐

        cmd.extend([
            "-c:v", "libx264",
            "-c:a", "aac",
            "-movflags", "faststart",    # Web 流媒体优化
            "-pix_fmt", "yuv420p",        # 浏览器兼容
            "-y",
        ])

        # 构建音频滤镜
        if use_bgm:
            # 混合人声和背景音乐，背景音乐音量从配置读取
            bgm_vol = settings.bgm_volume
            filter_complex = (
                f"[1:a]volume=1.0[voice];"  # 人声保持原音量
                f"[2:a]volume={bgm_vol},aloop=loop=-1:size=2e+09[bgm];"  # 背景音乐降低并循环
                f"[voice][bgm]amix=inputs=2:duration=first:dropout_transition=2[audioout]"  # 混合音频
            )
            cmd.extend(["-filter_complex", filter_complex, "-map", "0:v", "-map", "[audioout]"])
        else:
            cmd.extend(["-map", "0:v", "-map", "1:a"])

        # 处理时长差异
        if audio_duration > video_duration:
            extra_time = audio_duration - video_duration
            video_filter = f"[0:v]tpad=stop_mode=clone:stop_duration={extra_time}"
            if use_bgm:
                # 合并视频滤镜和音频滤镜
                existing_filter = cmd[cmd.index("-filter_complex") + 1]
                cmd[cmd.index("-filter_complex") + 1] = f"{video_filter};{existing_filter}"
            else:
                cmd.extend(["-filter_complex", video_filter])

        cmd.append(str(output_path))

        logger.info(f"FFmpeg 命令: {' '.join(cmd)}")

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise RuntimeError(f"FFmpeg 失败: {stderr.decode()}")

        # 验证输出时长
        output_duration = await get_media_duration(output_path)
        logger.info(f"最终视频生成: {output_path}, 时长: {output_duration:.2f}秒")

        # 上传到 MinIO
        from ...services.storage import get_storage_service
        storage = get_storage_service()

        minio_url = storage.upload_file(output_path, "video/mp4")
        logger.info(f"最终视频已上传到 MinIO: {minio_url}")

        return {
            "final_video_url": minio_url,
            "step": "done",
        }

    finally:
        # 清理临时文件
        for temp_path in [temp_video_path, temp_audio_path, output_path]:
            if temp_path and temp_path.exists():
                try:
                    temp_path.unlink()
                except Exception:
                    pass


def _get_background_music() -> str | None:
    """获取背景音乐文件路径"""
    import random

    bgm_dir = Path(__file__).parent.parent.parent.parent.parent / "assets" / "bgm"

    if not bgm_dir.exists():
        return None

    # 支持的音乐文件扩展名
    music_extensions = {".mp3", ".wav", ".m4a", ".aac", ".flac"}

    # 查找所有音乐文件
    music_files = [
        f for f in bgm_dir.iterdir()
        if f.is_file() and f.suffix.lower() in music_extensions
    ]

    if not music_files:
        logger.warning(f"背景音乐目录为空: {bgm_dir}")
        return None

    # 随机选择一首背景音乐
    selected = random.choice(music_files)
    logger.info(f"随机选择背景音乐: {selected.name}")
    return str(selected)
