"""
图像生成节点
"""
import logging
from typing import Literal

from langgraph.types import Send
from ...state import AgentState, Scene

logger = logging.getLogger(__name__)


def route_images_node(state: AgentState):
    """分发图像生成任务"""
    scenes = state.get("scenes", [])
    style_seed = state.get("style_seed", 0)

    logger.info(f"route_images_node: scenes count={len(scenes)}, style_seed={style_seed}")

    for scene in scenes:
        logger.info(f"  分发场景 {scene['id']}: {scene.get('text', '')[:30]}...")
        yield Send(
            "generate_image",
            {"scene": scene, "style_seed": style_seed}
        )


async def generate_image_node(task: dict) -> dict:
    """生成单个图像"""
    scene = task["scene"]
    style_seed = task["style_seed"]

    from ...services import get_image_service
    image_service = get_image_service()

    try:
        logger.info(f"开始生成图像 scene {scene['id']}: {scene['image_prompt'][:50]}...")
        image_url = await image_service.generate(
            prompt=scene["image_prompt"],
            seed=style_seed,
        )

        scene["image_url"] = image_url
        logger.info(f"图像生成成功 scene {scene['id']}: {image_url}")

        return {
            f"image_{scene['id']}": {
                "status": "completed",
                "image_url": image_url,
                "scene_id": scene["id"],
            }
        }

    except Exception as e:
        logger.error(f"图像生成失败 (scene {scene['id']}): {e}")
        return {
            f"image_{scene['id']}": {
                "status": "failed",
                "error": str(e),
                "scene_id": scene["id"],
            }
        }


async def aggregate_images_node(state: AgentState) -> dict:
    """聚合图像结果"""
    scenes = state.get("scenes", [])

    completed = 0
    for scene in scenes:
        task = state.get(f"image_{scene['id']}")
        if task and task["status"] == "completed":
            scene["image_url"] = task["image_url"]
            completed += 1

    logger.info(f"图像聚合: {completed}/{len(scenes)}")

    return {
        "completed_images": completed,
        "step": "animating" if completed > 0 else "failed",
    }


def should_continue_to_video(state: AgentState) -> Literal["continue", "skip"]:
    """判断是否继续到视频生成"""
    completed = state.get("completed_images", 0)
    total = state.get("total_images", 0)

    if completed >= total:
        return "continue"
    return "skip"
