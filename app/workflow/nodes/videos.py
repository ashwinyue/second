"""
视频生成节点
"""
import logging
from typing import Literal

from langgraph.types import Send
from ...state import AgentState, Scene

logger = logging.getLogger(__name__)


def route_videos_node(state: AgentState):
    """分发视频生成任务"""
    scenes = state.get("scenes", [])

    for scene in scenes:
        if scene.get("image_url"):
            yield Send(
                "generate_video",
                {"scene": scene}
            )


async def generate_video_node(task: dict) -> dict:
    """生成单个视频"""
    scene = task["scene"]
    image_url = scene.get("image_url", "")

    from ...services import get_video_service
    video_service = get_video_service()

    try:
        video_url = await video_service.generate(
            image_url=image_url,
            prompt=scene["image_prompt"],
            duration=scene["duration"],
        )

        scene["video_url"] = video_url

        return {
            f"video_{scene['id']}": {
                "status": "completed",
                "video_url": video_url,
                "scene_id": scene["id"],
            }
        }

    except Exception as e:
        logger.error(f"视频生成失败 (scene {scene['id']}): {e}")
        # 降级：使用图像
        return {
            f"video_{scene['id']}": {
                "status": "failed",
                "video_url": image_url,
                "scene_id": scene["id"],
            }
        }


async def aggregate_videos_node(state: AgentState) -> dict:
    """聚合视频结果"""
    scenes = state.get("scenes", [])

    completed = 0
    for scene in scenes:
        task = state.get(f"video_{scene['id']}")
        if task:
            scene["video_url"] = task["video_url"]
            if task["status"] == "completed":
                completed += 1

    logger.info(f"视频聚合: {completed}/{len(scenes)}")

    return {
        "completed_videos": completed,
        "step": "composing" if completed > 0 else "failed",
    }


def should_continue_to_compose(state: AgentState) -> Literal["continue", "skip"]:
    """判断是否继续到合成"""
    completed = state.get("completed_videos", 0)

    if completed > 0:
        return "continue"
    return "skip"
