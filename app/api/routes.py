"""
REST API 路由 - SSE 流式返回
"""
import logging
import json
import uuid
from typing import AsyncGenerator
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse, StreamingResponse

from .models import GenerationRequest, GenerationResponse, TaskStatus, HealthResponse
from ..workflow import create_graph
from ..state import AgentState
from ..config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["tasks"])


# ============================================================================
# SSE 流式生成端点
# ============================================================================

def _calculate_progress(state: AgentState) -> float:
    """根据当前状态计算进度"""
    step = state.get("step", "")

    # 步骤权重
    step_weights = {
        "init": 0.05,
        "writing": 0.15,
        "imaging": 0.40,
        "animating": 0.70,
        "composing": 0.90,
        "done": 1.0,
    }

    base_progress = step_weights.get(step, 0.0)

    # 图像生成阶段的子进度
    if step == "imaging":
        completed = state.get("completed_images", 0)
        total = state.get("total_images", 1)
        if total > 0:
            base_progress += (completed / total) * 0.2  # 20% 分配给图像生成

    # 视频生成阶段的子进度
    elif step == "animating":
        completed = state.get("completed_videos", 0)
        total = state.get("total_images", 1)
        if total > 0:
            base_progress += (completed / total) * 0.2  # 20% 分配给视频生成

    return min(base_progress, 0.99)  # 最高到 99%，完成时设为 100%


def _get_step_message(step: str) -> str:
    """获取步骤显示消息"""
    messages = {
        "init": "初始化...",
        "writing": "正在生成文案...",
        "imaging": "正在生成图像...",
        "animating": "正在生成视频动画...",
        "composing": "正在合成视频...",
        "done": "完成！",
    }
    return messages.get(step, "处理中...")


async def _stream_generation(
    topic: str,
    philosopher: str | None = None,
    science_type: str | None = None,
    style_preset: str = "dark_healing",
) -> AsyncGenerator[str, None]:
    """
    流式生成视频，通过 SSE 返回进度

    SSE 事件类型：
    - progress: 进度更新
    - scene: 场景数据更新（图片/视频生成完成）
    - done: 完成，返回最终视频 URL
    - error: 错误
    """
    task_id = uuid.uuid4().hex
    graph = create_graph()

    # 初始状态
    initial_state: AgentState = {
        "config": {
            "topic": topic,
            "philosopher": philosopher,
            "science_type": science_type,
            "style_preset": style_preset,
        },
        "step": "init",
    }

    config = {
        "configurable": {"thread_id": task_id}
    }

    logger.info(f"[SSE] 开始流式生成: task_id={task_id}, topic={topic}")

    try:
        # 发送初始事件
        yield _sse_event("init", {
            "task_id": task_id,
            "topic": topic,
        })

        # 流式执行工作流
        final_state = None
        event_count = 0

        async for event in graph.astream(initial_state, config):
            event_count += 1

            for node_name, state in event.items():
                if not isinstance(state, dict) or "step" not in state:
                    continue

                final_state = state
                step = state.get("step", "")
                progress = _calculate_progress(state)

                logger.info(f"[SSE] task_id={task_id}, node={node_name}, step={step}, progress={progress:.2f}")

                # 发送进度更新
                yield _sse_event("progress", {
                    "task_id": task_id,
                    "step": step,
                    "progress": progress,
                    "message": _get_step_message(step),
                })

                # 场景数据更新
                if "scenes" in state:
                    scenes = state["scenes"]
                    for scene in scenes:
                        scene_id = scene.get("id")
                        image_url = scene.get("image_url")
                        video_url = scene.get("video_url")

                        # 发送图像生成完成事件
                        if image_url:
                            yield _sse_event("scene", {
                                "task_id": task_id,
                                "scene_id": scene_id,
                                "type": "image",
                                "url": image_url,
                                "text": scene.get("text", ""),
                                "emotion": scene.get("emotion", ""),
                            })

                        # 发送视频生成完成事件
                        if video_url:
                            yield _sse_event("scene", {
                                "task_id": task_id,
                                "scene_id": scene_id,
                                "type": "video",
                                "url": video_url,
                            })

        # 处理最终状态
        if final_state:
            final_video_url = final_state.get("final_video_url")

            if final_video_url:
                # 提取文件名
                from pathlib import Path
                filename = Path(final_video_url).name

                yield _sse_event("done", {
                    "task_id": task_id,
                    "final_video_url": f"/outputs/final/{filename}",
                    "message": "视频生成完成！",
                })
            else:
                yield _sse_event("error", {
                    "task_id": task_id,
                    "message": "未能生成最终视频",
                })
        else:
            yield _sse_event("error", {
                "task_id": task_id,
                "message": "未能获取最终状态",
            })

        logger.info(f"[SSE] 流式生成完成: task_id={task_id}, events={event_count}")

    except Exception as e:
        logger.error(f"[SSE] 生成失败: task_id={task_id}, error={e}")
        yield _sse_event("error", {
            "task_id": task_id,
            "message": str(e),
        })


def _sse_event(event_type: str, data: dict) -> str:
    """构建 SSE 事件格式"""
    return f"event: {event_type}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@router.post(
    "/generate",
    summary="创建视频生成任务（SSE 流式返回）",
)
async def generate_video_stream(request: GenerationRequest):
    """
    创建视频生成任务，通过 SSE 流式返回进度

    **使用方式**:
    ```bash
    curl -N http://localhost:8001/api/v1/generate \
      -H "Content-Type: application/json" \
      -d '{"topic": "自由意志"}'
    ```

    **SSE 事件类型**:
    - `init`: 任务初始化，返回 task_id
    - `progress`: 进度更新 {step, progress, message}
    - `scene`: 场景数据更新 {scene_id, type, url}
    - `done`: 完成，返回最终视频 URL
    - `error`: 错误信息

    - **topic**: 视频主题（必需）
    - **philosopher**: 指定哲学家（可选）
    - **science_type**: 关联科学类型（可选）
    - **style_preset**: 风格预设，默认 dark_healing
    """
    return StreamingResponse(
        _stream_generation(
            topic=request.topic,
            philosopher=request.philosopher,
            science_type=request.science_type,
            style_preset=request.style_preset,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # 禁用 nginx 缓冲
        },
    )


# ============================================================================
# 其他 REST 端点
# ============================================================================

@router.get(
    "/videos/{filename}",
    summary="下载生成的视频",
)
async def download_video(filename: str) -> FileResponse:
    """
    下载生成的视频文件
    """
    settings = get_settings()
    video_path = settings.output_dir / "final" / filename

    if not video_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="视频文件不存在",
        )

    return FileResponse(
        path=video_path,
        media_type="video/mp4",
        filename=filename,
    )


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="健康检查",
)
async def health_check() -> HealthResponse:
    """
    检查服务健康状态和各服务可用性
    """
    settings = get_settings()

    # 简单检查配置是否完整
    services = {
        "llm": bool(settings.ark_api_key),
        "image": bool(settings.ark_api_key),
        "video": bool(settings.ark_api_key),
        "tts": bool(settings.tts_appid and settings.tts_access_token),
    }

    return HealthResponse(
        status="healthy" if all(services.values()) else "degraded",
        version="1.0.0",
        services=services,
    )
