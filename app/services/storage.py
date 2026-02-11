"""
MinIO 对象存储服务
"""
import logging
import hashlib
import urllib.parse
from pathlib import Path
from typing import BinaryIO, Optional

from minio import Minio
from minio.error import S3Error

from ..config import get_settings

logger = logging.getLogger(__name__)


class StorageService:
    """MinIO 对象存储服务"""

    def __init__(self):
        settings = get_settings()
        self.endpoint = settings.minio_endpoint
        self.access_key = settings.minio_access_key
        self.secret_key = settings.minio_secret_key
        self.bucket = settings.minio_bucket
        self.use_ssl = settings.minio_use_ssl
        self.public_url = settings.minio_public_url

        # 初始化 MinIO 客户端
        self.client = Minio(
            self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=self.use_ssl,
        )

        # 确保 bucket 存在
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        """确保 bucket 存在"""
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
                # 设置 bucket 为公开读取
                policy = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {"AWS": "*"},
                            "Action": ["s3:GetObject"],
                            "Resource": [f"arn:aws:s3:::{self.bucket}/*"],
                        }
                    ],
                }
                import json
                self.client.set_bucket_policy(self.bucket, json.dumps(policy))
                logger.info(f"创建 MinIO bucket: {self.bucket}")
            else:
                logger.info(f"MinIO bucket 已存在: {self.bucket}")
        except S3Error as e:
            logger.error(f"MinIO bucket 初始化失败: {e}")
            raise

    def _get_object_name(self, prefix: str, content: bytes | BinaryIO, ext: str = "") -> str:
        """生成对象名称（带缓存友好命名）"""
        if isinstance(content, bytes):
            content_hash = hashlib.md5(content).hexdigest()[:12]
        else:
            # 对于文件对象，使用位置信息作为 hash
            content_hash = hashlib.md5(str(content).encode()).hexdigest()[:12]

        timestamp = hashlib.md5(str(hash(content)).encode()).hexdigest()[:8]
        return f"{prefix}/{content_hash}-{timestamp}.{ext}"

    def upload_bytes(
        self,
        data: bytes,
        filename: str,
        content_type: str = "application/octet-stream",
    ) -> str:
        """
        上传字节数据到 MinIO

        Args:
            data: 字节数据
            filename: 文件名
            content_type: MIME 类型

        Returns:
            公开访问 URL
        """
        try:
            # 确定前缀和扩展名
            ext = Path(filename).suffix or ".bin"
            if "image" in content_type:
                prefix = "images"
            elif "video" in content_type:
                prefix = "videos"
            elif "audio" in content_type:
                prefix = "audio"
            else:
                prefix = "files"

            # 生成对象名
            object_name = self._get_object_name(prefix, data, ext.lstrip("."))

            # 上传
            from io import BytesIO
            self.client.put_object(
                self.bucket,
                object_name,
                BytesIO(data),
                length=len(data),
                content_type=content_type,
            )

            # 返回公开 URL
            url = f"{self.public_url}/{self.bucket}/{object_name}"
            logger.info(f"上传成功: {filename} -> {url}")
            return url

        except S3Error as e:
            logger.error(f"上传失败: {filename}, error={e}")
            raise

    def upload_file(
        self,
        file_path: str | Path,
        content_type: Optional[str] = None,
    ) -> str:
        """
        上传文件到 MinIO

        Args:
            file_path: 文件路径
            content_type: MIME 类型（可选，自动检测）

        Returns:
            公开访问 URL
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        # 读取文件
        data = file_path.read_bytes()

        # 自动检测 content_type
        if content_type is None:
            import mimetypes
            content_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"

        return self.upload_bytes(data, file_path.name, content_type)

    def delete_file(self, object_name: str) -> bool:
        """删除文件"""
        try:
            self.client.remove_object(self.bucket, object_name)
            logger.info(f"删除成功: {object_name}")
            return True
        except S3Error as e:
            logger.error(f"删除失败: {object_name}, error={e}")
            return False

    def get_presigned_url(self, object_name: str, expires: int = 3600) -> str:
        """获取预签名 URL（用于私有文件）"""
        try:
            return self.client.presigned_get_object(
                self.bucket,
                object_name,
                expires=expires,
            )
        except S3Error as e:
            logger.error(f"生成预签名 URL 失败: {object_name}, error={e}")
            raise


_storage_service: StorageService | None = None


def get_storage_service() -> StorageService:
    """获取存储服务单例"""
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService()
    return _storage_service
