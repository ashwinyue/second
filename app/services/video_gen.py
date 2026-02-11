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

    async def generate(
        self,
        image_url: str,
        prompt: str,
        duration: float = 5.0,
    ) -> str:
        """生成视频并上传到 MinIO"""
        # 创建任务（移除 duration 参数，该模型不支持）
        motion_prompt = f"{prompt}, --camerafixed false --watermark true"

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

            logger.info(f"视频任务状态: task_id={task_id}, status={result.status}")

            if result.status == "succeeded":
                # 检查响应结构 - 可能是 result.content.video_url 或直接在 result 上
                video_url = None

                # 方法1: 检查 content 属性
                if hasattr(result, 'content') and result.content:
                    if hasattr(result.content, 'video_url'):
                        video_url = result.content.video_url
                    # 或者 content 本身就是 URL 字符串
                    elif isinstance(result.content, str) and result.content.startswith('http'):
                        video_url = result.content
                # 方法2: 直接检查 result 上的属性
                elif hasattr(result, 'video_url'):
                    video_url = result.video_url
                # 方法3: 检查 content 对象中的 video_url 字段
                elif hasattr(result, 'content') and hasattr(result.content, '__dict__'):
                    content_dict = result.content.__dict__
                    video_url = content_dict.get('video_url')

                if not video_url:
                    logger.error(f"视频任务成功但无法提取video_url: task_id={task_id}, result类型={type(result)}")
                    # 打印完整结果结构用于调试
                    import pprint
                    logger.error(f"完整结果: {pprint.pformat(result)}")
                    raise Exception("视频生成成功但无法提取video_url")

                logger.info(f"视频生成成功，开始下载并上传到 MinIO: {video_url}")
                # 下载并上传到 MinIO
                return await self._download_and_upload(video_url, task_id)

            elif result.status == "failed":
                error_msg = getattr(result, 'error', '未知错误')
                logger.error(f"视频任务失败: task_id={task_id}, error={error_msg}")
                raise Exception(f"视频生成失败: {error_msg}")
            elif result.status in ("pending", "processing"):
                logger.debug(f"视频任务处理中: task_id={task_id}, status={result.status}")
            else:
                logger.warning(f"视频任务未知状态: task_id={task_id}, status={result.status}")

            await asyncio.sleep(3)

        raise TimeoutError("视频生成超时")

    async def _download_and_upload(self, url: str, task_id: str) -> str:
        """下载视频并上传到 MinIO（不保存到本地）"""
        async with httpx.AsyncClient(timeout=120.0) as client:
            r = await client.get(url)
            r.raise_for_status()
            video_data = r.content

        # 直接上传到 MinIO
        from .storage import get_storage_service
        storage = get_storage_service()

        filename = f"{task_id[:12]}.mp4"
        public_url = storage.upload_bytes(video_data, filename, "video/mp4")
        logger.info(f"视频已上传到 MinIO: {public_url}")
        return public_url


_video_service: VideoGenService | None = None


def get_video_service() -> VideoGenService:
    """获取视频服务单例"""
    global _video_service
    if _video_service is None:
        _video_service = VideoGenService()
    return _video_service
