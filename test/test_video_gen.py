"""
豆包视频生成 API 测试
"""
import os
import time
from volcenginesdkarkruntime import Ark
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_video_generation():
    """测试视频生成"""

    # 初始化客户端
    client = Ark(
        base_url="https://ark.cn-beijing.volces.com/api/v3",
        api_key=os.getenv("ARK_API_KEY"),
    )

    print("===== 开始测试视频生成 =====")

    # 创建视频生成任务
    print("\n1. 创建视频任务...")
    create_result = client.content_generation.tasks.create(
        model="doubao-seedance-1-0-pro-fast-251015",
        content=[
            {
                "type": "text",
                "text": "无人机以极快速度穿越复杂障碍或自然奇观，带来沉浸式飞行体验 --resolution 1080p --duration 3 --camerafixed false --watermark true"
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": "https://ark-project.tos-cn-beijing.volces.com/doc_image/seepro_i2v.png"
                }
            }
        ]
    )

    print(f"任务ID: {create_result.id}")
    # create_result 返回的是 ContentGenerationTaskID，没有 status 属性
    print(f"创建任务类型: {type(create_result)}")

    # 轮询任务状态
    task_id = create_result.id
    max_wait = 300  # 5分钟
    start_time = time.time()

    print("\n2. 轮询任务状态...")
    while time.time() - start_time < max_wait:
        get_result = client.content_generation.tasks.get(task_id=task_id)
        status = get_result.status

        print(f"状态: {status}", end="")

        if status == "succeeded":
            print(" ✅ 成功！")
            print("\n===== 任务成功 =====")
            print(f"完整响应: {get_result}")

            # 检查响应结构
            if hasattr(get_result, 'output'):
                print(f"\n✅ 有 output 属性")
                if hasattr(get_result.output, 'video'):
                    print(f"✅ 有 video 属性")
                    if hasattr(get_result.output.video, 'url'):
                        video_url = get_result.output.video.url
                        print(f"✅ 视频URL: {video_url}")
                    else:
                        print(f"❌ video 无 url 属性")
                        print(f"video 对象: {get_result.output.video}")
                else:
                    print(f"❌ output 无 video 属性")
                    print(f"output 对象: {get_result.output}")
            else:
                print(f"❌ 无 output 属性")
                print(f"可访问的属性: {dir(get_result)}")

            return True

        elif status == "failed":
            print(" ❌ 失败！")
            print(f"\n===== 任务失败 =====")
            if hasattr(get_result, 'error'):
                print(f"错误: {get_result.error}")
            else:
                print(f"响应: {get_result}")
            return False

        else:
            print(" ...等待中")
            time.sleep(3)

    print("\n❌ 超时！")
    return False


if __name__ == "__main__":
    test_video_generation()
