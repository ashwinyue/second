"""
LangGraph 工作流构建
"""
import logging
import uuid

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import RetryPolicy

from ..state import AgentState
from .nodes import (
    init_node,
    writer_node,
    route_images_node,
    generate_image_node,
    aggregate_images_node,
    route_videos_node,
    generate_video_node,
    aggregate_videos_node,
    compose_node,
    narrator_node,
    add_audio_node,
)

logger = logging.getLogger(__name__)


# ============================================================================
# 条件路由函数
# ============================================================================

def should_continue_to_video(state: AgentState) -> str:
    """判断是否继续到视频生成"""
    completed = state.get("completed_images", 0)
    total = state.get("total_images", 0)

    if completed >= total:
        return "continue"
    return "skip"


def should_continue_to_compose(state: AgentState) -> str:
    """判断是否继续到合成"""
    completed = state.get("completed_videos", 0)

    if completed > 0:
        return "continue"
    return "skip"


# ============================================================================
# 工作流构建
# ============================================================================

def create_graph():
    """创建 LangGraph 工作流"""
    workflow = StateGraph(AgentState)

    # 重试策略
    retry_policy = RetryPolicy(
        max_attempts=3,
        initial_interval=1.0,
        backoff_factor=2.0,
        jitter=True,
    )

    # 添加节点
    workflow.add_node("init", init_node)
    workflow.add_node("writer", writer_node)

    workflow.add_node("generate_image", generate_image_node, retry_policy=retry_policy)
    workflow.add_node("aggregate_images", aggregate_images_node)

    workflow.add_node("route_videos", route_videos_node)  # 路由节点
    workflow.add_node("generate_video", generate_video_node, retry_policy=retry_policy)
    workflow.add_node("aggregate_videos", aggregate_videos_node)

    workflow.add_node("compose", compose_node)
    workflow.add_node("narrator", narrator_node)
    workflow.add_node("add_audio", add_audio_node)

    # 添加边
    workflow.add_edge(START, "init")
    workflow.add_edge("init", "writer")

    # 图像生成（并发）
    workflow.add_conditional_edges("writer", route_images_node, ["generate_image"])
    workflow.add_edge("generate_image", "aggregate_images")

    # 判断是否继续视频生成
    workflow.add_conditional_edges(
        "aggregate_images",
        should_continue_to_video,
        {"continue": "route_videos", "skip": END},
    )

    # 视频生成（并发）
    workflow.add_conditional_edges("route_videos", route_videos_node, ["generate_video"])
    workflow.add_edge("generate_video", "aggregate_videos")

    # 判断是否继续合成
    workflow.add_conditional_edges(
        "aggregate_videos",
        should_continue_to_compose,
        {"continue": "compose", "skip": END},
    )

    # 合成后进行语音合成
    workflow.add_edge("compose", "narrator")
    workflow.add_edge("narrator", "add_audio")
    workflow.add_edge("add_audio", END)

    # 编译
    checkpointer = MemorySaver()
    return workflow.compile(checkpointer=checkpointer)


async def generate_video(
    topic: str,
    philosopher: str | None = None,
    science_type: str | None = None,
    style_preset: str = "dark_healing",
    thread_id: str | None = None,
) -> dict:
    """生成视频"""
    graph = create_graph()

    config = {
        "configurable": {"thread_id": thread_id or uuid.uuid4().hex}
    }

    initial_state: AgentState = {
        "config": {
            "topic": topic,
            "philosopher": philosopher,
            "science_type": science_type,
            "style_preset": style_preset,
        },
        "step": "init",
    }

    result = await graph.ainvoke(initial_state, config)
    return result
