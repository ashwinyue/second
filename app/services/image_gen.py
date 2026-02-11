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
        self.model = "doubao-seedream-4-5-251128"  # 升级到 Seedream 4.5 以支持角色一致性

    @staticmethod
    def _image_to_base64(image_path: str) -> str:
        """将图像文件转换为 base64 编码"""
        import base64
        with open(image_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')

    async def generate(
        self,
        prompt: str,
        seed: int,
        size: str = "1920x1920",
        ref_image_list: list[str] | None = None,
    ) -> tuple[str, str]:
        """
        生成图像并上传到 MinIO

        Args:
            prompt: 图像生成提示词
            seed: 随机种子（用于风格一致性）
            size: 图像尺寸 (支持: "1080x1920", "2K" 等)
            ref_image_list: 参考图像路径列表（用于角色一致性）

        Returns:
            (cloud_url, minio_url) - 云端临时URL和MinIO公开URL
            - cloud_url: 火山引擎云存储临时URL（24小时有效，用于视频生成）
            - minio_url: 本地MinIO公开URL（用于前端展示）
        """
        # 基础 API 参数（官方标准调用方式）
        api_params = {
            "model": self.model,
            "prompt": prompt,
            "size": size,
            "seed": seed,
            "sequential_image_generation": "disabled",  # 单图模式
            "response_format": "url",
            "stream": False,
            "watermark": True,
        }

        # 添加参考图（用于角色一致性）- 需要通过 extra_body 传递
        if ref_image_list:
            base64_images = [self._image_to_base64(img) for img in ref_image_list]
            api_params["extra_body"] = {
                "ref_image_list": base64_images,
            }
            logger.info(f"使用 {len(ref_image_list)} 张参考图进行角色一致性生成")

        # 调用 API
        logger.info(f"调用图像生成 API: {prompt[:50]}...")
        response = self.client.images.generate(**api_params)

        cloud_url = response.data[0].url
        logger.info(f"图像 API 返回 URL: {cloud_url}")

        # 下载图片内容
        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.get(cloud_url)
            r.raise_for_status()
            image_data = r.content

        # 直接上传到 MinIO（不保存到本地）
        from .storage import get_storage_service
        storage = get_storage_service()

        # 生成文件名
        ref_hash = "".join([hashlib.md5(p.encode()).hexdigest()[:4] for p in (ref_image_list or [])])
        prompt_hash = hashlib.md5(f"{prompt}_{seed}_{ref_hash}".encode()).hexdigest()[:12]
        filename = f"{prompt_hash}.png"

        public_url = storage.upload_bytes(image_data, filename, "image/png")
        logger.info(f"图像已上传到 MinIO: {public_url}")
        return cloud_url, public_url


_image_service: ImageGenService | None = None


def get_image_service() -> ImageGenService:
    """获取图像服务单例"""
    global _image_service
    if _image_service is None:
        _image_service = ImageGenService()
    return _image_service
