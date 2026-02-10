"""
火山引擎豆包 TTS 2.0 语音合成测试脚本
"""
import base64
import json
import logging
import uuid
from pathlib import Path

import requests

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_tts_synthesis(
    appid: str,
    access_token: str,
    cluster: str,
    voice_type: str,
    text: str,
    output_path: str = "test_output.mp3"
) -> bool:
    """
    测试语音合成 (HTTP 方式)
    """
    host = "openspeech.bytedance.com"
    api_url = f"https://{host}/api/v1/tts"

    # 同时使用 Authorization header 和 X-Appid/X-Token headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer; {access_token}",
        "X-Appid": appid,
        "X-Token": access_token,
        "X-Uid": "user-001"
    }

    # 构建请求（无需 secret_key）
    request_json = {
        "app": {
            "appid": appid,
            "token": access_token,
            "cluster": cluster
        },
        "user": {
            "uid": "user-001"
        },
        "audio": {
            "voice_type": voice_type,
            "encoding": "mp3",
            "speed_ratio": 0.88,
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

        # 检查是否返回音频数据
        if response.status_code == 200 and response.headers.get("Content-Type", "").startswith("audio"):
            # 直接保存音频数据
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_bytes(response.content)
            logger.info(f"音频已保存: {output_file}, 大小: {len(response.content)} bytes")
            return True

        result = response.json()
        logger.info(f"响应内容: {json.dumps(result, indent=2, ensure_ascii=False)}")

        # 检查 JSON 响应中的 data 字段
        if "data" in result:
            audio_data = base64.b64decode(result["data"])
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
    # 用户提供的参数
    appid = "5940468387"
    access_token = "4C2XUpuozDw3QQoAqTQU7YM-aiTzxuvu"
    cluster = "volcano_tts"
    voice_type = "zh_male_dayi_saturn_bigtts"  # 男声达意

    # 测试文本
    test_texts = [
        "人类为什么只有在无限接近幸福的时候，才是最幸福的。",
        "今天天气真不错，适合出去走走。",
        "人工智能技术正在快速发展，语音合成变得越来越自然。",
    ]

    print("\n" + "=" * 60)
    print("火山引擎豆包 TTS 2.0 语音合成测试")
    print("=" * 60)

    # 运行测试
    for i, text in enumerate(test_texts, 1):
        print(f"\n--- 测试 {i}/{len(test_texts)} ---")
        output_path = f"outputs/audio/test_{i}.mp3"

        success = test_tts_synthesis(
            appid=appid,
            access_token=access_token,
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
