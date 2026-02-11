"""
配置管理
"""
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""

    ark_api_key: str = Field(..., alias="ARK_API_KEY")

    # TTS 配置
    tts_appid: str = Field(..., alias="VOLC_TTS_APPID")
    tts_access_token: str = Field(..., alias="VOLC_TTS_ACCESS_TOKEN")
    tts_secret_key: str = Field(..., alias="VOLC_TTS_SECRET_KEY")
    tts_cluster: str = Field(default="volcano_tts", alias="VOLC_TTS_CLUSTER")
    tts_endpoint: str = Field(default="https://openspeech.bytedance.com/api/v1/tts", alias="VOLC_TTS_ENDPOINT")
    tts_voice: str = Field(default="zh_female_jitangnv_saturn_bigtts", alias="TTS_VOICE")

    # LLM 配置
    llm_model: str = "doubao-seed-1-8-251228"
    image_model: str = "doubao-seedream-3-0-t2i-250415"
    video_model: str = "doubao-seedance-1-0-pro-fast-251015"

    output_dir: Path = Field(default=Path("./outputs"))

    # 背景音乐配置
    bgm_enabled: bool = Field(default=True, alias="BGM_ENABLED")
    bgm_volume: float = Field(default=0.2, alias="BGM_VOLUME")  # 背景音乐音量 (0.0-1.0)

    # MinIO 对象存储配置
    minio_endpoint: str = Field(default="localhost:9000", alias="MINIO_ENDPOINT")
    minio_access_key: str = Field(default="minioadmin", alias="MINIO_ACCESS_KEY")
    minio_secret_key: str = Field(default="minioadmin", alias="MINIO_SECRET_KEY")
    minio_bucket: str = Field(default="dear-assets", alias="MINIO_BUCKET")
    minio_use_ssl: bool = Field(default=False, alias="MINIO_USE_SSL")
    minio_public_url: str = Field(default="http://localhost:9000", alias="MINIO_PUBLIC_URL")

    # 数据库配置
    database_url: str = Field(
        default="postgresql+asyncpg://dear:dear_password@localhost:5432/dear_agent",
        alias="DATABASE_URL"
    )
    database_echo: bool = Field(default=False, alias="DATABASE_ECHO")

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # 忽略额外的环境变量


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
        _settings.output_dir.mkdir(parents=True, exist_ok=True)
    return _settings
