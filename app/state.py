"""
状态定义
LangGraph TypedDict + Annotated Reducer
"""
from typing import TypedDict, NotRequired, Required


class Scene(TypedDict):
    """单个场景"""
    id: int
    text: str
    type: str  # hook/theory/science/analogy/twist/sublime
    duration: float
    emotion: str
    image_prompt: str
    image_url: NotRequired[str]
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
