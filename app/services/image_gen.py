"""
图像生成服务 (文生图)
"""
import logging
import hashlib
from pathlib import Path
import httpx

from volcenginesdkarkruntime import Ark
from ..config import get_settings

logger = logging.getLogger(__name__)


class ImageGenService:
    """图像生成服务"""

    def __init__(self):
        settings = get_settings()
        self.client = Ark(
            base_url="https://ark.cn-beijing.volces.com/api/v3",
            api_key=settings.ark_api_key,
        )
        self.model = "doubao-seedream-3-0-t2i-250415"
        self.output_dir = settings.output_dir / "images"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def generate(
        self,
        prompt: str,
        seed: int,
        size: str = "1080x1920",
    ) -> str:
        """生成图像"""
        # 生成缓存文件名
        prompt_hash = hashlib.md5(f"{prompt}_{seed}".encode()).hexdigest()[:12]
        output_path = self.output_dir / f"{prompt_hash}.png"

        if output_path.exists():
            logger.info(f"使用缓存图像: {output_path.name}")
            return str(output_path)

        # 调用 API
        logger.info(f"调用图像生成 API: {prompt[:50]}...")
        response = self.client.images.generate(
            model=self.model,
            prompt=prompt,
            size=size,
            guidance_scale=2.5,
            seed=seed,
            watermark=True,
        )

        image_url = response.data[0].url
        logger.info(f"图像 API 返回 URL: {image_url}")

        # 下载
        logger.info(f"下载图像到: {output_path}")
        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.get(image_url)
            r.raise_for_status()
            output_path.write_bytes(r.content)

        logger.info(f"图像生成完成: {output_path}")
        return str(output_path)


_image_service: ImageGenService | None = None


def get_image_service() -> ImageGenService:
    """获取图像服务单例"""
    global _image_service
    if _image_service is None:
        _image_service = ImageGenService()
    return _image_service
