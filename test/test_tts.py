"""
火山引擎 Seed-TTS 语音合成测试脚本

使用 HTTP 协议（不是 WebSocket）
"""
import base64
import json
import logging
import uuid
from pathlib import Path

import requests
from dotenv import load_dotenv

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_tts_synthesis(
    appid: str,
    access_token: str,
    secret_key: str,
    cluster: str,
    voice_type: str,
    text: str,
    output_path: str = "test_output.mp3"
) -> bool:
    """
    测试语音合成 (HTTP 方式)

    Args:
        appid: 应用 ID
        access_token: 访问令牌
        secret_key: 密钥
        cluster: 集群 ID (实例 ID)
        voice_type: 音色类型
        text: 要转换的文本
        output_path: 输出文件路径

    Returns:
        是否成功
    """
    host = "openspeech.bytedance.com"
    api_url = f"https://{host}/api/v1/tts"

    headers = {"Authorization": f"Bearer; {access_token}"}

    # 构建请求
    request_json = {
        "app": {
            "appid": appid,
            "token": access_token,
            "cluster": cluster
        },
        "user": {
            "uid": str(uuid.uuid4())
        },
        "audio": {
            "voice_type": voice_type,
            "encoding": "mp3",
            "speed_ratio": 1.0,
            "volume_ratio": 1.0,
            "pitch_ratio": 1.0,
        },
        "request": {
            "reqid": str(uuid.uuid4()),
            "text": text,
            "text_type": "plain",
            "operation": "query"
        }
    }

    logger.info(f"连接到: {api_url}")
    logger.info(f"APP ID: {appid}")
    logger.info(f"Cluster: {cluster}")
    logger.info(f"Voice Type: {voice_type}")
    logger.info(f"Text: {text}")

    try:
        response = requests.post(
            api_url,
            json=request_json,
            headers=headers,
            timeout=30
        )

        logger.info(f"响应状态码: {response.status_code}")

        result = response.json()
        logger.info(f"响应内容: {json.dumps(result, indent=2, ensure_ascii=False)}")

        # 检查响应
        if response.status_code == 200 and "data" in result:
            # 解码 base64 音频数据
            audio_data = base64.b64decode(result["data"])

            # 保存音频文件
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_bytes(audio_data)

            logger.info(f"音频已保存: {output_file}, 大小: {len(audio_data)} bytes")
            return True
        else:
            logger.error(f"请求失败: {result}")
            return False

    except Exception as e:
        logger.error(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    # 加载环境变量
    load_dotenv()

    # 从环境变量获取配置
    import os
    appid = os.getenv("VOLC_TTS_APPID")
    access_token = os.getenv("VOLC_TTS_ACCESS_TOKEN")
    secret_key = os.getenv("VOLC_TTS_SECRET_KEY")
    cluster = os.getenv("VOLC_TTS_CLUSTER", "volcano_tts")
    voice_type = os.getenv("VOLC_TTS_VOICE_TYPE", "zh_female_qingxin")

    # 验证配置
    if not appid or appid == "your_tts_appid_here":
        logger.error("VOLC_TTS_APPID 未配置")
        return

    if not access_token or access_token == "your_access_token_here":
        logger.error("VOLC_TTS_ACCESS_TOKEN 未配置")
        return

    # 测试文本
    test_texts = [
        "你好，这是火山引擎语音合成测试。",
        "今天天气真不错。",
        "人工智能技术正在快速发展。",
    ]

    print("\n" + "=" * 60)
    print("火山引擎 Seed-TTS 语音合成测试")
    print("=" * 60)

    # 运行测试
    for i, text in enumerate(test_texts, 1):
        print(f"\n--- 测试 {i}/{len(test_texts)} ---")
        output_path = f"outputs/audio/test_{i}.mp3"

        success = test_tts_synthesis(
            appid=appid,
            access_token=access_token,
            secret_key=secret_key,
            cluster=cluster,
            voice_type=voice_type,
            text=text,
            output_path=output_path
        )

        if success:
            print(f"✅ 测试 {i} 成功: {output_path}")
        else:
            print(f"❌ 测试 {i} 失败")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
