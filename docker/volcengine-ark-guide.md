# 火山引擎 Ark API 客户端初始化

## 环境准备

首先安装 Ark SDK：

```bash
pip install volcengine-python-sdk[ark]
```

## 配置 API Key

> **豆包 API Key**：一个 Key 可在多个模型间通用使用
在.key文件中  
请将 API Key 存储在环境变量中，配置方法详见：[官方文档](https://www.volcengine.com/docs/82379/1399008)

### 方式一：直接设置环境变量

```bash
export ARK_API_KEY="your-api-key-here"
```

### 方式二：使用 .env 文件

创建 `.env` 文件：

```bash
# .env
ARK_API_KEY=your-api-key-here
```

然后使用 `python-dotenv` 加载：

```bash
pip install python-dotenv
```

```python
from dotenv import load_dotenv
load_dotenv()  # 加载 .env 文件
```

## 客户端初始化

```python
import os
from volcenginesdkarkruntime import Ark

# 从环境变量中获取 API Key
api_key = os.getenv('ARK_API_KEY')

# 初始化客户端
client = Ark(
    base_url='https://ark.cn-beijing.volces.com/api/v3',
    api_key=api_key,
)
```

## 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `base_url` | API 基础地址，根据地域配置 | `https://ark.cn-beijing.volces.com/api/v3` |
| `api_key` | API 认证密钥，从环境变量读取 | - |

---

# 模型调用示例

## 1. 视觉理解模型（图文理解）

**模型 ID**: `doubao-seed-1-8-251228`

支持图片 + 文本输入，理解图片内容并回答问题。

```python
response = client.responses.create(
    model="doubao-seed-1-8-251228",
    input=[
        {
            "role": "user",
            "content": [
                {
                    "type": "input_image",
                    "image_url": "https://example.com/image.png"
                },
                {
                    "type": "input_text",
                    "text": "你看见了什么？"
                },
            ],
        }
    ]
)
print(response)
```

---

## 2. 图生视频模型

**模型 ID**: `doubao-seedance-1-5-pro-251215`

根据图片和文本描述生成视频。

### 参数说明

| 参数 | 说明 |
|------|------|
| `--duration` | 视频时长（秒） |
| `--camerafixed` | 是否固定摄像头 |
| `--watermark` | 是否添加水印 |

---

## 3. 文生图模型

**模型 ID**: `doubao-seedream-3-0-t2i-250415`

根据文本提示词生成图片，支持 seed 参数保证生成一致性。

### 参数说明

| 参数 | 说明 |
|------|------|
| `prompt` | 文本提示词 |
| `size` | 图片尺寸（如 `512x512`、`1080x1920`） |
| `guidance_scale` | 提示词引导强度（1-10） |
| `seed` | 随机种子，相同种子生成相同结果 |
| `watermark` | 是否添加水印 |

```python
import os
from volcenginesdkarkruntime import Ark

client = Ark(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key=os.environ.get("ARK_API_KEY"),
)

imagesResponse = client.images.generate(
    model="doubao-seedream-3-0-t2i-250415",
    prompt="鱼眼镜头，一只猫咪的头部，画面呈现出猫咪的五官因为拍摄方式扭曲的效果。",
    size="512x512",
    guidance_scale=2.5,
    seed=12345,
    watermark=True
)

print(imagesResponse.data[0].url)
```

---

## 4. 图像编辑模型（可选）

**模型 ID**: `doubao-seedance-1-0-pro-fast-251015`

性价比高的视频生成模型，支持轮询查询任务状态。

```python
import os
import time
from volcenginesdkarkruntime import Ark

client = Ark(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key=os.environ.get("ARK_API_KEY"),
)

if __name__ == "__main__":
    # 创建任务
    print("----- create request -----")
    create_result = client.content_generation.tasks.create(
        model="doubao-seedance-1-0-pro-fast-251015",
        content=[
            {
                "type": "text",
                "text": "无人机以极快速度穿越复杂障碍或自然奇观 --resolution 1080p --duration 5 --camerafixed false --watermark true"
            },
            {
                # 可选：首帧图片（图生视频）
                "type": "image_url",
                "image_url": {
                    "url": "https://example.com/image.png"
                }
            }
        ]
    )
    print(create_result)

    # 轮询查询任务状态
    print("----- polling task status -----")
    task_id = create_result.id
    while True:
        get_result = client.content_generation.tasks.get(task_id=task_id)
        status = get_result.status
        if status == "succeeded":
            print("----- task succeeded -----")
            print(get_result)
            break
        elif status == "failed":
            print("----- task failed -----")
            print(f"Error: {get_result.error}")
            break
        else:
            print(f"Current status: {status}, Retrying after 3 seconds...")
            time.sleep(3)
```

### 相关文档

- [查询视频生成任务列表](https://www.volcengine.com/docs/82379/1521675)
- [取消或删除视频生成任务](https://www.volcengine.com/docs/82379/1521720)

---

## 5. 图像编辑模型（可选）

**模型 ID**: `doubao-seededit-3-0-i2i-250628`

根据文本指令编辑图片内容（图生图）。

```python
import os
from volcenginesdkarkruntime import Ark

client = Ark(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key=os.environ.get("ARK_API_KEY"),
)

imagesResponse = client.images.generate(
    model="doubao-seededit-3-0-i2i-250628",
    prompt="改成爱心形状的泡泡",
    image="https://example.com/image.jpeg",
    seed=123,
    guidance_scale=5.5,
    size="adaptive",
    watermark=True
)

print(imagesResponse.data[0].url)
```

---

## 6. 大模型语音合成（TTS）

> **官方文档**：[大模型语音合成API](https://www.volcengine.com/docs/6561/1329505?lang=zh)
>
> **注意**：大模型语音合成使用 **WebSocket 二进制协议**，支持流式语音合成。

### 环境准备

```bash
pip install websockets>=14.0
```

### 配置说明

在 `.env` 文件中配置：

```bash
# 大模型语音合成配置 (WebSocket 二进制协议)
VOLC_TTS_APPID=your_tts_appid_here          # 从火山方舟控制台获取
VOLC_TTS_ACCESS_TOKEN=your_access_token_here # Access Token
VOLC_TTS_CLUSTER=your_cluster_here          # 集群 ID
VOLC_TTS_VOICE_TYPE=BV034_streaming        # 音色类型
VOLC_TTS_HOST=openspeech.bytedance.com
VOLC_TTS_ENDPOINT=wss://openspeech.bytedance.com/api/v1/tts/ws_binary
```

**参数获取**：
- **APP ID**、**Access Token**、**Cluster** 需要在 [火山方舟控制台](https://ark.cn-beijing.volces.com/) 获取
- 在控制台开通「大模型语音合成」服务后创建应用获取

### 二进制协议说明

火山引擎大模型语音合成使用专有的二进制协议格式：

**协议头部（4字节）**：
```
| 字节 | 说明 |
|------|------|
| 0 | protocol_version(4bit) + header_size(4bit) |
| 1 | message_type(4bit) + message_type_specific_flags(4bit) |
| 2 | serialization_method(4bit) + message_compression(4bit) |
| 3 | reserved(8bit) |
```

**消息类型**：
- `0b0001` - Full client request (完整客户端请求)
- `0b1011` - Audio only server response (音频服务器响应)
- `0b1100` - Frontend server response (前端服务器响应)
- `0b1111` - Error message from server (服务器错误消息)

### 调用示例

```python
import asyncio
import gzip
import json
import uuid
import websockets

# ===== 二进制协议常量 =====
PROTOCOL_VERSION = 0b0001
HEADER_SIZE = 0b0001

# Message Type
FULL_CLIENT_REQUEST = 0b0001
AUDIO_ONLY_SERVER_RESPONSE = 0b1011

# Message Type Specific Flags
NO_SEQUENCE = 0b0000
POS_SEQUENCE = 0b0001
NEG_SEQUENCE = 0b0010

# Serialization
JSON_SERIALIZATION = 0b0001

# Compression
GZIP_COMPRESSION = 0b0001


def generate_header(
    message_type=FULL_CLIENT_REQUEST,
    message_type_specific_flags=NO_SEQUENCE,
    serialization_method=JSON_SERIALIZATION,
    compression_type=GZIP_COMPRESSION
) -> bytes:
    """生成协议头部"""
    header = bytearray()
    header.append((PROTOCOL_VERSION << 4) | HEADER_SIZE)
    header.append((message_type << 4) | message_type_specific_flags)
    header.append((serialization_method << 4) | compression_type)
    header.append(0x00)  # reserved
    return bytes(header)


def build_request(
    appid: str,
    token: str,
    cluster: str,
    voice_type: str,
    text: str,
    encoding: str = "mp3"
) -> bytes:
    """构建完整请求"""
    request_json = {
        "app": {
            "appid": appid,
            "token": token,
            "cluster": cluster
        },
        "user": {
            "uid": str(uuid.uuid4())
        },
        "audio": {
            "voice_type": voice_type,
            "encoding": encoding,
            "speed_ratio": 1.0,
            "volume_ratio": 1.0,
            "pitch_ratio": 1.0,
        },
        "request": {
            "reqid": str(uuid.uuid4()),
            "text": text,
            "text_type": "plain",
            "operation": "submit"
        }
    }

    # 压缩 JSON 负载
    payload_bytes = gzip.compress(json.dumps(request_json).encode('utf-8'))

    # 构建完整请求
    full_request = bytearray(generate_header())
    full_request.extend(len(payload_bytes).to_bytes(4, 'big'))  # payload size
    full_request.extend(payload_bytes)

    return bytes(full_request)


async def parse_response(res: bytes) -> dict:
    """解析服务器响应"""
    # 解析头部
    protocol_version = res[0] >> 4
    header_size = res[0] & 0x0f
    message_type = res[1] >> 4
    message_type_specific_flags = res[1] & 0x0f

    payload_start = header_size * 4
    payload = res[payload_start:]

    result = {
        'is_last_package': False,
        'audio_data': None
    }

    if message_type == AUDIO_ONLY_SERVER_RESPONSE:
        if message_type_specific_flags & 0x01:
            # 有序列号
            sequence_number = int.from_bytes(payload[:4], "big", signed=True)
            payload_size = int.from_bytes(payload[4:8], "big", signed=False)
            audio_data = payload[8:8+payload_size]

            result['audio_data'] = audio_data

            if sequence_number < 0:
                result['is_last_package'] = True

        return result

    elif message_type == 0b1111:  # Error message
        code = int.from_bytes(payload[:4], "big", signed=False)
        msg_size = int.from_bytes(payload[4:8], "big", signed=False)
        error_msg = payload[8:8+msg_size]
        if res[2] & 0x0f == GZIP_COMPRESSION:
            error_msg = gzip.decompress(error_msg)
        error_msg = error_msg.decode('utf-8')
        raise Exception(f"TTS Error [{code}]: {error_msg}")

    return result


async def text_to_speech(
    appid: str,
    token: str,
    cluster: str,
    voice_type: str,
    text: str,
    encoding: str = "mp3",
    host: str = "openspeech.bytedance.com"
) -> bytes:
    """
    大模型语音合成

    :param appid: 应用 ID
    :param token: 访问令牌
    :param cluster: 集群 ID
    :param voice_type: 音色类型
    :param text: 要转换的文本
    :param encoding: 音频编码格式 (mp3/wav)
    :param host: 服务器地址
    :return: 音频数据 (bytes)
    """
    api_url = f"wss://{host}/api/v1/tts/ws_binary"
    headers = {"Authorization": f"Bearer; {token}"}

    async with websockets.connect(api_url, extra_headers=headers, max_size=100_000_000) as ws:
        # 发送请求
        request = build_request(appid, token, cluster, voice_type, text, encoding)
        await ws.send(request)

        # 接收音频数据
        audio_data = bytearray()

        while True:
            res = await ws.recv()
            result = await parse_response(res)

            if result['audio_data']:
                audio_data.extend(result['audio_data'])

            if result['is_last_package']:
                break

        return bytes(audio_data)


async def save_audio(audio_data: bytes, filename: str) -> str:
    """保存音频数据到文件"""
    with open(filename, "wb") as f:
        f.write(audio_data)
    return filename


# ===== 使用示例 =====
if __name__ == "__main__":
    async def main():
        # 从环境变量加载配置
        import os
        from dotenv import load_dotenv
        load_dotenv()

        appid = os.getenv("VOLC_TTS_APPID")
        token = os.getenv("VOLC_TTS_ACCESS_TOKEN")
        cluster = os.getenv("VOLC_TTS_CLUSTER")
        voice_type = os.getenv("VOLC_TTS_VOICE_TYPE", "BV034_streaming")

        # 合成语音
        audio_data = await text_to_speech(
            appid=appid,
            token=token,
            cluster=cluster,
            voice_type=voice_type,
            text="你好，这是火山引擎大模型语音合成测试。",
            encoding="mp3"
        )

        # 保存音频文件
        filename = await save_audio(audio_data, "output.mp3")
        print(f"音频已保存到: {filename}")

    asyncio.run(main())
```

### 常用音色类型

| 音色代码 | 说明 | 适用场景 |
|---------|------|---------|
| `BV034_streaming` | 大模型流式音色（女声） | 实时对话、助手 |
| `BV002_streaming` | 大模型流式音色（男声） | 实时对话、助手 |
| `zh_female_qingxin` | 女声清新 | 通用、客服 |
| `zh_male_chunhou` | 男声醇厚 | 新闻、纪录片 |

> 更多音色请参考火山方舟控制台的音色列表

### 请求参数说明

| 参数 | 说明 | 必填 |
|------|------|------|
| `appid` | 应用 ID | 是 |
| `token` | 访问令牌 (Access Token) | 是 |
| `cluster` | 集群 ID | 是 |
| `voice_type` | 音色类型 | 是 |
| `encoding` | 音频编码：`mp3`、`wav` | 是 |
| `speed_ratio` | 语速（0.2-2.0，默认1.0） | 否 |
| `volume_ratio` | 音量（0.1-3.0，默认1.0） | 否 |
| `pitch_ratio` | 音调（0.1-3.0，默认1.0） | 否 |

### 协议模块

完整的二进制协议实现位于：`docs/volcengine_binary_demo/protocols/`

核心功能：
- `generate_header()` - 生成协议头部
- `build_request()` - 构建完整请求
- `parse_response()` - 解析服务器响应

---

# 模型清单

| 功能 | 模型 ID | 类型 | SDK |
|------|---------|------|-----|
| 视觉理解 | `doubao-seed-1-8-251228` | 多模态 | Ark |
| 文生图 | `doubao-seedream-3-0-t2i-250415` | 图像生成 | Ark |
| 图像编辑（可选） | `doubao-seededit-3-0-i2i-250628` | 图像编辑 | Ark |
| 图生视频（Pro） | `doubao-seedance-1-5-pro-251215` | 视频生成 | Ark |
| 图生视频（经济） | `doubao-seedance-1-0-pro-fast-251015` | 视频生成 | Ark |
| 语音合成 | - | TTS | WebSocket |

---

# 协议模块

语音合成需要使用二进制协议模块，源码位于：`docs/volcengine_binary_demo/protocols/`

核心功能：
- `full_client_request()` - 发送完整客户端请求
- `receive_message()` - 接收服务器消息
- `Message` - 二进制消息封装类
