"""
图像生成节点 - 支持角色一致性
"""
import logging
from typing import Literal

from langgraph.types import Send
from ...state import AgentState, Scene
from ...style_base import build_character_card

logger = logging.getLogger(__name__)


def route_images_node(state: AgentState):
    """
    分发图像生成任务

    支持两种模式：
    - 并行模式（默认）：所有场景并行生成，使用角色卡提示词保证一致性
    - 串行模式：按顺序生成，后一场景使用前一场景的图像作为参考图

    支持多风格系统
    """
    scenes = state.get("scenes", [])
    style_seed = state.get("style_seed", 0)
    config = state.get("config", {})

    # 获取风格配置
    style_name = config.get("style", "camus")

    # 角色一致性配置
    enable_character_consistency = config.get("enable_character_consistency", True)
    character_gender = config.get("character_gender", "中性")
    character_age = config.get("character_age", "成年")
    character_style = config.get("character_style", "极简")
    serial_generation = config.get("serial_generation", False)  # 是否启用串行链式生成

    # 生成角色卡（传入visual_style参数）
    character_card = None
    if enable_character_consistency:
        character_card = build_character_card(
            gender=character_gender,
            age=character_age,
            style=character_style,
            visual_style=style_name,  # 传递视觉风格
        )
        logger.info(f"角色卡已生成: {character_gender}, {character_age}, {character_style}风格, 视觉风格={style_name}")

    logger.info(f"route_images_node: scenes={len(scenes)}, seed={style_seed}, style={style_name}, "
                f"character_consistency={enable_character_consistency}, serial={serial_generation}")

    # 返回 Send 对象列表
    sends = []
    for scene in scenes:
        logger.info(f"  分发场景 {scene['id']}: {scene.get('text', '')[:30]}...")
        sends.append(Send(
            "generate_image",
            {
                "scene": scene,
                "style_seed": style_seed,
                "style": style_name,  # 传递风格参数
                "character_card": character_card,
                "serial_generation": serial_generation,
            }
        ))
    return sends


async def generate_image_node(task: dict) -> dict:
    """
    生成单个图像

    支持角色一致性：
    - 角色卡模式：在提示词中嵌入角色描述
    - 参考图模式：使用前一场景的图像作为参考图（需要串行生成）

    支持多风格：
    - camus/healing/knowledge/humor/growth/minimal 等风格
    """
    scene = task["scene"]
    style_seed = task["style_seed"]
    scene_id = str(scene["id"])
    character_card = task.get("character_card")
    style_name = task.get("style", "camus")  # 获取风格，默认为camus
    serial_generation = task.get("serial_generation", False)
    ref_image_path = task.get("ref_image_path")  # 串行模式下的参考图路径

    from ...services import get_image_service
    from ...style_base import build_stylized_prompt_with_character
    image_service = get_image_service()

    try:
        # 构建增强提示词（含角色卡）
        enhanced_prompt = build_stylized_prompt_with_character(
            base_prompt=scene["image_prompt"],
            emotion=scene.get("emotion", "共鸣"),
            character_card=character_card,
            style=style_name,  # 传递风格参数
            include_camera=True,
        )

        # 准备参考图列表
        ref_image_list = [ref_image_path] if ref_image_path else None

        logger.info(f"开始生成图像 scene {scene_id}: {scene['image_prompt'][:50]}...")
        if ref_image_list:
            logger.info(f"  使用参考图: {ref_image_path}")

        # 获取云 URL（用于视频生成）和 MinIO URL（用于前端展示）
        cloud_url, minio_url = await image_service.generate(
            prompt=enhanced_prompt,
            seed=style_seed,
            ref_image_list=ref_image_list,
        )

        logger.info(f"图像生成成功 scene {scene_id}: cloud_url={cloud_url[:80]}..., minio_url={minio_url}")

        return {
            "image_tasks": {
                scene_id: {
                    "status": "completed",
                    "image_url": minio_url,          # 前端展示用 MinIO URL
                    "image_cloud_url": cloud_url,    # 视频生成用云 URL
                    "scene_id": scene["id"],
                }
            }
        }

    except Exception as e:
        logger.error(f"图像生成失败 (scene {scene_id}): {e}", exc_info=True)
        return {
            "image_tasks": {
                scene_id: {
                    "status": "failed",
                    "error": str(e),
                    "scene_id": scene["id"],
                }
            }
        }


async def aggregate_images_node(state: AgentState) -> dict:
    """聚合图像结果"""
    scenes = state.get("scenes", [])
    image_tasks = state.get("image_tasks", {})

    completed = 0
    updated_scenes = []

    logger.info(f"聚合图像结果: scenes={len(scenes)}, image_tasks={list(image_tasks.keys())}")

    for scene in scenes:
        scene_id = str(scene["id"])
        updated_scene = dict(scene)

        # 从 image_tasks 中查找对应的结果
        task_result = image_tasks.get(scene_id)
        if task_result and task_result.get("status") == "completed":
            updated_scene["image_url"] = task_result.get("image_url")
            updated_scene["image_cloud_url"] = task_result.get("image_cloud_url", "")
            completed += 1
            logger.info(f"场景 {scene_id} 图像已完成")
        elif task_result:
            logger.warning(f"场景 {scene_id} 图像生成失败: {task_result.get('error')}")
        else:
            logger.warning(f"场景 {scene_id} 没有找到图像任务结果")

        updated_scenes.append(updated_scene)

    logger.info(f"图像聚合完成: {completed}/{len(scenes)}")

    return {
        "scenes": updated_scenes,
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
