"""
视频生成服务
"""
import logging
import time
import asyncio
from pathlib import Path
import httpx

from volcenginesdkarkruntime import Ark
from ..config import get_settings

logger = logging.getLogger(__name__)


class VideoGenService:
    """视频生成服务"""

    def __init__(self):
        settings = get_settings()
        self.client = Ark(
            base_url="https://ark.cn-beijing.volces.com/api/v3",
            api_key=settings.ark_api_key,
        )
        self.model = "doubao-seedance-1-0-pro-fast-251015"
        self.output_dir = settings.output_dir / "videos"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def generate(
        self,
        image_url: str,
        prompt: str,
        duration: float = 5.0,
    ) -> str:
        """生成视频"""
        # 创建任务
        motion_prompt = f"{prompt}, --duration {duration} --camerafixed false --watermark true"

        response = self.client.content_generation.tasks.create(
            model=self.model,
            content=[
                {"type": "text", "text": motion_prompt},
                {"type": "image_url", "image_url": {"url": image_url}},
            ]
        )

        task_id = response.id

        # 轮询状态
        max_wait = 300  # 5分钟
        start_time = time.time()

        while time.time() - start_time < max_wait:
            result = self.client.content_generation.tasks.get(task_id=task_id)

            if result.status == "succeeded":
                video_url = result.output.video.url
                # 下载
                return await self._download(video_url)
            elif result.status == "failed":
                raise Exception(f"视频生成失败: {result.error}")

            await asyncio.sleep(3)

        raise TimeoutError("视频生成超时")

    async def _download(self, url: str) -> str:
        """下载视频"""
        import uuid
        video_id = uuid.uuid4().hex[:12]
        output_path = self.output_dir / f"{video_id}.mp4"

        async with httpx.AsyncClient(timeout=120.0) as client:
            r = await client.get(url)
            r.raise_for_status()
            output_path.write_bytes(r.content)

        return str(output_path)


_video_service: VideoGenService | None = None


def get_video_service() -> VideoGenService:
    """获取视频服务单例"""
    global _video_service
    if _video_service is None:
        _video_service = VideoGenService()
    return _video_service
