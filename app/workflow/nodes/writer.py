"""
文案生成节点
"""
import logging

from ...state import AgentState, Scene
from ...style import build_stylized_prompt

logger = logging.getLogger(__name__)

WRITER_SYSTEM = """你是哲学科普视频文案创作者。

输出 JSON 格式：
```json
{
  "scenes": [
    {
      "id": 1,
      "text": "文案内容",
      "type": "hook|theory|science|analogy|twist|sublime",
      "duration": 2.0,
      "emotion": "困惑|顿悟|震撼|温柔|沉重|共鸣",
      "image_prompt": "图像提示词"
    }
  ]
}
```

要求：
- 2-3 句（测试模式），每句 2-3 秒
- 每句话都具有画面感
- 避免 AI 味词汇
"""


async def writer_node(state: AgentState) -> dict:
    """文案生成节点"""
    config = state["config"]
    topic = config["topic"]
    style_seed = state["style_seed"]

    from ...services import get_llm_service
    llm = get_llm_service()

    user_prompt = f"""
主题：{topic}
哲学家：{config.get('philosopher', '不限')}
科学类型：{config.get('science_type', '不限')}
风格：{config.get('style_preset', '暗黑治愈')}

请生成 2-3 句哲学科普视频文案（测试模式）。
"""

    try:
        result = await llm.generate_json(
            prompt=user_prompt,
            system_prompt=WRITER_SYSTEM,
        )

        scenes = []
        for i, s in enumerate(result.get("scenes", []), 1):
            # 增强图像提示词
            enhanced_prompt = build_stylized_prompt(
                s["image_prompt"],
                s.get("emotion", "中性")
            )

            scene: Scene = {
                "id": s["id"],
                "text": s["text"],
                "type": s["type"],
                "duration": float(s["duration"]),
                "emotion": s["emotion"],
                "image_prompt": enhanced_prompt,
            }
            scenes.append(scene)

        logger.info(f"文案生成成功: {len(scenes)} 句")

        return {
            "step": "imaging",
            "scenes": scenes,
            "total_images": len(scenes),
        }

    except Exception as e:
        logger.error(f"文案生成失败: {e}")
        return {
            "step": "failed",
            "errors": [f"文案生成失败: {str(e)}"],
        }
