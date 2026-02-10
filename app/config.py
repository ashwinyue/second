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
    tts_cluster: str = Field(default="volcano_tts", alias="VOLC_TTS_CLUSTER")
    tts_endpoint: str = Field(default="https://openspeech.bytedance.com/api/v1/tts", alias="VOLC_TTS_ENDPOINT")
    tts_voice: str = Field(default="zh_male_dayi_saturn_bigtts", alias="TTS_VOICE")

    # LLM 配置
    llm_model: str = "doubao-seed-1-8-251228"
    image_model: str = "doubao-seedream-3-0-t2i-250415"
    video_model: str = "doubao-seedance-1-0-pro-fast-251015"

    output_dir: Path = Field(default=Path("./outputs"))

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
