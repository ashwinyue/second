"""
状态定义
LangGraph TypedDict + Annotated Reducer
"""
from typing import TypedDict, NotRequired, Required, Annotated
from typing_extensions import deprecated
from operator import add


def merge_image_tasks(left: dict | None, right: dict | None) -> dict:
    """合并图像任务结果"""
    if not left:
        return right or {}
    if not right:
        return left
    return {**left, **right}


def merge_video_tasks(left: dict | None, right: dict | None) -> dict:
    """合并视频任务结果"""
    if not left:
        return right or {}
    if not right:
        return left
    return {**left, **right}


class Scene(TypedDict):
    """单个场景"""
    id: int
    text: str
    type: str  # hook/theory/science/analogy/twist/sublime
    duration: float
    emotion: str
    image_prompt: str
    image_url: NotRequired[str]  # 本地路径
    image_cloud_url: NotRequired[str]  # 云存储 URL（用于视频生成）
    video_url: NotRequired[str]


class AgentState(TypedDict):
    """Agent 主状态"""
    config: Required[dict]
    step: str
    scenes: NotRequired[list[Scene]]
    style_seed: NotRequired[int]
    completed_images: NotRequired[int]
    total_images: NotRequired[int]
    completed_videos: NotRequired[int]
    total_videos: NotRequired[int]
    composed_video_url: NotRequired[str]
    audio_url: NotRequired[str]
    final_video_url: NotRequired[str]
    errors: NotRequired[list[str]]
    # 图像任务结果（使用 reducer 合并）
    image_tasks: Annotated[dict, merge_image_tasks]
    # 视频任务结果（使用 reducer 合并）
    video_tasks: Annotated[dict, merge_video_tasks]
