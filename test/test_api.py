#!/usr/bin/env python3
"""
API 测试脚本
"""
import requests
import json

BASE_URL = "http://localhost:8001"

print("=" * 60)
print("DEAR Agent API 测试")
print("=" * 60)

# 1. 健康检查
print("\n1. 健康检查")
response = requests.get(f"{BASE_URL}/api/v1/health")
print(f"状态码: {response.status_code}")
print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")

# 2. 创建视频生成任务
print("\n2. 创建视频生成任务")
response = requests.post(
    f"{BASE_URL}/api/v1/generate",
    json={
        "topic": "自由意志是否存在",
        "philosopher": "萨特",
        "science_type": "神经科学",
        "style_preset": "dark_healing"
    }
)
print(f"状态码: {response.status_code}")
result = response.json()
print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")

task_id = result.get("task_id")
print(f"\n任务 ID: {task_id}")

# 3. 查询任务状态
if task_id:
    print("\n3. 查询任务状态")
    import time
    time.sleep(2)  # 等待任务启动

    response = requests.get(f"{BASE_URL}/api/v1/tasks/{task_id}")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")

# 4. 流式对话测试
print("\n4. 流式对话测试")
response = requests.post(
    f"{BASE_URL}/api/v1/chat/stream",
    json={
        "message": "我想做一个关于自由意志的视频"
    },
    stream=True
)
print(f"状态码: {response.status_code}")
print("SSE 响应:")
for line in response.iter_lines():
    if line:
        print(f"  {line.decode('utf-8')}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
print(f"\n访问 API 文档: {BASE_URL}/docs")
