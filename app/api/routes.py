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
        "init": 0.02,
        "writing": 0.10,
        "imaging": 0.30,
        "animating": 0.55,
        "composing": 0.70,
        "narrating": 0.85,
        "adding_audio": 0.95,
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
        "imaging": "正在生成场景图像...",
        "animating": "正在生成分镜视频...",
        "composing": "正在合并视频片段...",
        "narrating": "正在生成配音...",
        "adding_audio": "正在合并配音到视频...",
        "done": "完成！",
    }
    return messages.get(step, "处理中...")


async def _stream_generation(
    topic: str,
    style: str = "minimal",
    theme: str | None = None,
    philosopher: str | None = None,  # 向后兼容
    science_type: str | None = None,  # 向后兼容
    style_preset: str | None = None,  # 向后兼容
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

    # 处理向后兼容的参数映射
    final_style = style
    final_theme = theme

    if philosopher:
        # 如果指定了philosopher，使用camus风格
        final_style = "camus"
        final_theme = final_theme or philosopher
    elif style_preset:
        # style_preset映射到style
        final_style = style_preset

    # 初始状态
    initial_state: AgentState = {
        "config": {
            "topic": topic,
            "style": final_style,
            "theme": final_theme or "",
            # 向后兼容的旧参数
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
        writing_sent = False  # 标记文案是否已发送

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

                # 文案生成完成事件（首次进入 imaging 步骤时发送）
                if step == "imaging" and "scenes" in state and not writing_sent:
                    writing_sent = True
                    scenes = state["scenes"]
                    yield _sse_event("writing_done", {
                        "task_id": task_id,
                        "scenes": [
                            {
                                "id": s.get("id"),
                                "text": s.get("text", ""),
                                "type": s.get("type", ""),
                                "emotion": s.get("emotion", ""),
                            }
                            for s in scenes
                        ],
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
                                "scene_type": "image",
                                "url": image_url,
                                "text": scene.get("text", ""),
                                "emotion": scene.get("emotion", ""),
                            })

                        # 发送视频生成完成事件
                        if video_url:
                            yield _sse_event("scene", {
                                "task_id": task_id,
                                "scene_id": scene_id,
                                "scene_type": "video",
                                "url": video_url,
                            })

        # 处理最终状态
        if final_state:
            final_video_url = final_state.get("final_video_url")

            if final_video_url:
                # 直接返回 MinIO URL
                yield _sse_event("done", {
                    "task_id": task_id,
                    "final_video_url": final_video_url,
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
      -d '{"topic": "生命的意义", "style": "camus", "theme": "荒诞"}'
    ```

    **SSE 事件类型**:
    - `init`: 任务初始化，返回 task_id
    - `progress`: 进度更新 {step, progress, message}
    - `scene`: 场景数据更新 {scene_id, type, url}
    - `done`: 完成，返回最终视频 URL
    - `error`: 错误信息

    **请求参数**:
    - **topic**: 视频主题（必需）
    - **style**: 风格名称（默认 minimal）
      - camus: 加缪荒诞哲学 - 深度拷问、诗意克制
      - healing: 温暖治愈 - 亲切陪伴、温柔鼓励
      - knowledge: 硬核科普 - 权威数据、逻辑清晰
      - humor: 幽默搞笑 - 反转套路、轻松调侃
      - growth: 成长觉醒 - 认知升级、行动导向
      - minimal: 极简金句 - 短小精悍、直击人心
    - **theme**: 可选的子主题（用于某些风格的细分）
    - **philosopher**: [向后兼容] 指定哲学家（映射到camus风格）
    - **science_type**: [向后兼容] 关联科学类型
    """
    return StreamingResponse(
        _stream_generation(
            topic=request.topic,
            style=request.style,
            theme=request.theme,
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

    返回可用的风格列表
    """
    settings = get_settings()

    # 简单检查配置是否完整
    services = {
        "llm": bool(settings.ark_api_key),
        "image": bool(settings.ark_api_key),
        "video": bool(settings.ark_api_key),
        "tts": bool(settings.tts_appid and settings.tts_access_token),
    }

    from ..style import get_available_styles
    available_styles = get_available_styles()

    return HealthResponse(
        status="healthy" if all(services.values()) else "degraded",
        version="2.0.0",
        services=services,
        available_styles=available_styles,
    )
