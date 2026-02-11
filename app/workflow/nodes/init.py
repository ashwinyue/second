"""
初始化节点
"""
import logging

from ...state import AgentState
from ...style_base import generate_style_seed

logger = logging.getLogger(__name__)


async def init_node(state: AgentState) -> dict:
    """初始化节点"""
    config = state["config"]
    topic = config["topic"]

    # 生成风格种子
    style_seed = generate_style_seed(topic)

    logger.info(f"初始化: topic={topic}, seed={style_seed}")

    return {
        "step": "writing",
        "style_seed": style_seed,
        "completed_images": 0,
        "total_images": 0,
        "completed_videos": 0,
        "errors": [],
    }
