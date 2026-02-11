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

    # 返回 Send 对象列表
    sends = []
    for scene in scenes:
        # 只对有云存储 URL 的场景生成视频
        if scene.get("image_cloud_url"):
            sends.append(Send(
                "generate_video",
                {"scene": scene}
            ))
    return sends


async def generate_video_node(task: dict) -> dict:
    """生成单个视频"""
    scene = task["scene"]
    # 使用云存储 URL（火山引擎可以访问）
    image_url = scene.get("image_cloud_url", "")

    from ...services import get_video_service
    video_service = get_video_service()

    # 测试模式：限制视频时长为 2 秒
    test_duration = min(scene.get("duration", 2.0), 2.0)

    try:
        logger.info(f"开始生成视频 scene {scene['id']}, cloud_url={image_url[:50] if image_url else 'None'}...")
        video_url = await video_service.generate(
            image_url=image_url,
            prompt=scene["image_prompt"],
            duration=test_duration,
        )

        logger.info(f"视频生成成功 scene {scene['id']}: {video_url}")

        return {
            "video_tasks": {
                str(scene['id']): {
                    "status": "completed",
                    "video_url": video_url,
                    "scene_id": scene["id"],
                }
            }
        }

    except Exception as e:
        logger.error(f"视频生成失败 (scene {scene['id']}): {e}", exc_info=True)
        return {
            "video_tasks": {
                str(scene['id']): {
                    "status": "failed",
                    "error": str(e),
                    "scene_id": scene["id"],
                }
            }
        }


async def aggregate_videos_node(state: AgentState) -> dict:
    """聚合视频结果"""
    scenes = state.get("scenes", [])
    video_tasks = state.get("video_tasks", {})

    completed = 0
    updated_scenes = []

    logger.info(f"聚合视频结果: scenes={len(scenes)}, video_tasks={list(video_tasks.keys())}")

    for scene in scenes:
        scene_id = str(scene["id"])
        updated_scene = dict(scene)

        task_result = video_tasks.get(scene_id)
        if task_result and task_result.get("status") == "completed":
            updated_scene["video_url"] = task_result.get("video_url")
            completed += 1
            logger.info(f"场景 {scene_id} 视频已完成")
        else:
            logger.warning(f"场景 {scene_id} 视频生成失败或未完成")

        updated_scenes.append(updated_scene)

    logger.info(f"视频聚合完成: {completed}/{len(scenes)}")

    return {
        "scenes": updated_scenes,
        "completed_videos": completed,
        "step": "composing" if completed > 0 else "failed",
    }


def should_continue_to_compose(state: AgentState) -> Literal["continue", "skip"]:
    """判断是否继续到合成"""
    completed = state.get("completed_videos", 0)

    if completed > 0:
        return "continue"
    return "skip"
