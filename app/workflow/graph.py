"""
LangGraph 工作流构建
"""
import logging
import uuid

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import RetryPolicy, Send

from ..state import AgentState
from .nodes import (
    init_node,
    writer_node,
    generate_image_node,
    aggregate_images_node,
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

def route_images(state: AgentState):
    """分发图像生成任务 - 返回 Send 对象列表或字符串"""
    scenes = state.get("scenes", [])
    style_seed = state.get("style_seed", 0)

    if not scenes:
        return END

    # 为每个场景创建一个 Send 对象
    return [Send("generate_image", {"scene": s, "style_seed": style_seed}) for s in scenes]


def route_videos(state: AgentState):
    """分发视频生成任务 - 返回 Send 对象列表或字符串"""
    scenes = state.get("scenes", [])

    # 只为有图像的场景创建视频
    scenes_with_images = [s for s in scenes if s.get("image_url")]

    if not scenes_with_images:
        return END

    return [Send("generate_video", {"scene": s}) for s in scenes_with_images]


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

    workflow.add_node("generate_video", generate_video_node, retry_policy=retry_policy)
    workflow.add_node("aggregate_videos", aggregate_videos_node)

    workflow.add_node("compose", compose_node)
    workflow.add_node("narrator", narrator_node)
    workflow.add_node("add_audio", add_audio_node)

    # 添加边
    workflow.add_edge(START, "init")
    workflow.add_edge("init", "writer")

    # 图像生成（并发 - 使用 map-reduce 模式）
    workflow.add_conditional_edges("writer", route_images, ["generate_image"])
    workflow.add_edge("generate_image", "aggregate_images")

    # 视频生成（并发 - 使用 map-reduce 模式）
    workflow.add_conditional_edges("aggregate_images", route_videos, ["generate_video"])
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
    style: str = "minimal",
    theme: str | None = None,
    philosopher: str | None = None,  # 向后兼容
    science_type: str | None = None,  # 向后兼容
    style_preset: str | None = None,  # 向后兼容
    thread_id: str | None = None,
) -> dict:
    """
    生成视频

    Args:
        topic: 视频主题
        style: 风格名称（camus/healing/knowledge/humor/growth/minimal）
        theme: 可选的子主题
        philosopher: 向后兼容参数（映射到camus风格）
        science_type: 向后兼容参数
        style_preset: 向后兼容参数（映射到style）
        thread_id: 会话ID

    Returns:
        生成结果字典
    """
    graph = create_graph()

    config = {
        "configurable": {"thread_id": thread_id or uuid.uuid4().hex}
    }

    # 处理向后兼容的参数映射
    final_style = style
    if philosopher:
        # 如果指定了philosopher，使用camus风格
        final_style = "camus"
        theme = theme or philosopher
    elif style_preset:
        # style_preset映射到style
        final_style = style_preset

    initial_state: AgentState = {
        "config": {
            "topic": topic,
            "style": final_style,
            "theme": theme or "",
            # 向后兼容的旧参数
            "philosopher": philosopher,
            "science_type": science_type,
            "style_preset": style_preset,
        },
        "step": "init",
    }

    result = await graph.ainvoke(initial_state, config)
    return result
