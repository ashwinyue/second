"""
TTS 服务 - 火山引擎豆包 TTS 2.0 语音合成
使用 HTTP 协议
"""
import base64
import hashlib
import hmac
import json
import logging
import time
import uuid
import httpx
from pathlib import Path
from typing import Optional

from ..config import get_settings

logger = logging.getLogger(__name__)


class TTSService:
    """语音合成服务"""

    def __init__(self):
        settings = get_settings()
        self.appid = settings.tts_appid
        self.access_token = settings.tts_access_token
        self.secret_key = settings.tts_secret_key
        self.cluster = settings.tts_cluster
        self.endpoint = settings.tts_endpoint or "https://openspeech.bytedance.com/api/v1/tts"

        # 默认配置 - 女声音色
        self.voice_type = settings.tts_voice or "zh_female_jitangnv_saturn_bigtts"
        self.encoding = "mp3"
        self.speed_ratio = 0.88  # 哲学科普推荐语速
        self.volume_ratio = 1.0
        self.pitch_ratio = 1.0

    def _generate_signature(self, reqid: str, timestamp: str) -> str:
        """生成签名"""
        # 签名字符串格式: appid + reqid + timestamp + cluster
        sign_str = f"{self.appid}{reqid}{timestamp}{self.cluster}"
        # 使用 secret_key 进行 HMAC-SHA256 签名
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            sign_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature

    async def synthesize(
        self,
        text: str,
        voice_type: Optional[str] = None,
        speed_ratio: Optional[float] = None,
    ) -> str:
        """
        合成语音并上传到 MinIO

        Args:
            text: 要转换的文本
            voice_type: 音色（可选）
            speed_ratio: 语速（可选）

        Returns:
            MinIO 公开访问 URL
        """
        if voice_type:
            self.voice_type = voice_type
        if speed_ratio is not None:
            self.speed_ratio = speed_ratio

        reqid = str(uuid.uuid4())
        timestamp = str(int(time.time()))

        # 生成签名
        signature = self._generate_signature(reqid, timestamp)

        # 构建请求
        request_json = {
            "app": {
                "appid": self.appid,
                "token": self.access_token,
                "cluster": self.cluster,
            },
            "user": {
                "uid": "user-001",
            },
            "audio": {
                "voice_type": self.voice_type,
                "encoding": self.encoding,
                "speed_ratio": self.speed_ratio,
                "volume_ratio": self.volume_ratio,
                "pitch_ratio": self.pitch_ratio,
            },
            "request": {
                "reqid": reqid,
                "text": text,
                "text_type": "plain",
                "operation": "query",
            },
        }

        # 构建请求头 - 使用 Authorization 头部（注意分号后有空格）
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer; {self.access_token}",
        }

        logger.info(f"TTS 请求: voice_type={self.voice_type}, text_length={len(text)}")

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.endpoint,
                    json=request_json,
                    headers=headers,
                )

                logger.info(f"TTS 响应: status={response.status_code}")

                if response.status_code != 200:
                    error_data = response.json()
                    raise Exception(f"TTS 服务错误: {error_data}")

                result = response.json()

                if result.get("code") != 3000:
                    error_msg = result.get("message", "未知错误")
                    raise Exception(f"TTS 合成失败: {error_msg}")

                # 解码 base64 音频数据
                audio_data = base64.b64decode(result["data"])

                if len(audio_data) == 0:
                    raise Exception("生成的音频数据为空")

                logger.info(f"音频生成成功, 大小: {len(audio_data)} bytes")

                # 直接上传到 MinIO
                from .storage import get_storage_service
                storage = get_storage_service()

                filename = f"{reqid}.mp3"
                minio_url = storage.upload_bytes(audio_data, filename, "audio/mpeg")
                logger.info(f"音频已上传到 MinIO: {minio_url}")

                return minio_url

        except httpx.HTTPError as e:
            logger.error(f"HTTP 请求失败: {e}")
            raise Exception(f"TTS 连接失败: {e}")
        except Exception as e:
            logger.error(f"TTS 合成失败: {e}")
            raise


_tts_service: TTSService | None = None


def get_tts_service() -> TTSService:
    """获取 TTS 服务单例"""
    global _tts_service
    if _tts_service is None:
        _tts_service = TTSService()
    return _tts_service
