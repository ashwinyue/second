"""
文案生成节点 - 多风格系统支持
支持加缪荒诞哲学、温暖治愈、硬核科普、幽默搞笑、成长觉醒、极简金句等多种风格
集成黄金3秒钩子理论和爆款文案框架
"""
import logging
import random

from ...state import AgentState, Scene
from ...style_base import (
    build_stylized_prompt,
    build_system_prompt,
    get_available_styles,
    get_style_config,
)
from ...style.xiaohongshu import CamusStyleAdapter
from ...style.templates import (
    build_camus_opening_prompt,
    CamusEndingGenerator,
    CamusTemplateGenerator,
)
from ...style.frameworks import (
    FrameworkBuilder,
    GOLDEN_3S_HOOKS,
    CTA_HOOKS,
)
from ...style.presets import STYLE_PRESETS

logger = logging.getLogger(__name__)


def _get_hook_template(hook_type: str) -> str:
    """获取钩子模板"""
    if hook_type in GOLDEN_3S_HOOKS:
        return random.choice(GOLDEN_3S_HOOKS[hook_type]["templates"])
    return random.choice(GOLDEN_3S_HOOKS["curiosity"]["templates"])


def _get_cta_hook(cta_type: str = "question") -> str:
    """获取互动钩子"""
    if cta_type in CTA_HOOKS:
        return random.choice(CTA_HOOKS[cta_type])
    return random.choice(CTA_HOOKS["question"])


async def writer_node(state: AgentState) -> dict:
    """
    文案生成节点 - 多风格系统支持

    支持的风格：
    - camus: 加缪荒诞哲学 - 深度拷问、诗意克制
    - healing: 温暖治愈 - 亲切陪伴、温柔鼓励
    - knowledge: 硬核科普 - 权威数据、逻辑清晰
    - humor: 幽默搞笑 - 反转套路、轻松调侃
    - growth: 成长觉醒 - 认知升级、行动导向
    - minimal: 极简金句 - 短小精悍、直击人心

    配置参数：
    - style: 风格名称（默认 minimal）
    - theme: 主题（用于某些风格的子主题）
    """
    config = state["config"]
    topic = config["topic"]
    style_seed = state["style_seed"]

    # 获取风格配置
    style_name = config.get('style', 'minimal')
    theme = config.get('theme', '')  # 主题（用于某些风格）

    # 验证风格是否存在
    if style_name not in STYLE_PRESETS:
        logger.warning(f"风格 '{style_name}' 不存在，使用默认风格 'minimal'")
        style_name = 'minimal'

    style_config = STYLE_PRESETS[style_name]

    # 获取系统提示词
    system_prompt = build_system_prompt(style_name) or build_system_prompt("camus")

    from ...services import get_llm_service
    llm = get_llm_service()

    # 构建用户提示词
    user_prompt = _build_user_prompt(
        topic=topic,
        style=style_name,
        theme=theme,
        style_config=style_config,
    )

    try:
        result = await llm.generate_json(
            prompt=user_prompt,
            system_prompt=system_prompt,
        )

        scenes = []
        scene_list = result.get("scenes", [])

        for i, s in enumerate(scene_list, 1):
            original_text = s["text"]
            emotion = s.get("emotion", "共鸣")
            scene_type = s.get("type", "hook")

            # 风格适配（对于需要适配的风格）
            adapted_text = _adapt_text_by_style(
                original_text=original_text,
                emotion=emotion,
                style_name=style_name,
                is_last_scene=(i == len(scene_list)),
                style_config=style_config,
            )

            # 增强图像提示词
            enhanced_prompt = build_stylized_prompt(
                s["image_prompt"],
                emotion,
                style=style_name,
            )

            scene: Scene = {
                "id": s["id"],
                "text": adapted_text,
                "type": s["type"],
                "duration": float(s["duration"]),
                "emotion": emotion,
                "image_prompt": enhanced_prompt,
            }
            scenes.append(scene)

        logger.info(f"{style_name} 风格文案生成成功: {len(scenes)} 句 (主题={theme or style_name})")

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


def _build_user_prompt(
    topic: str,
    style: str,
    theme: str,
    style_config,
) -> str:
    """构建用户提示词"""
    parts = []

    # 添加风格特定的钩子指导
    if style_config.hook_types:
        hook_type = random.choice(style_config.hook_types)
        hook_template = _get_hook_template(hook_type)
        parts.append(f"【开头钩子参考】\n{hook_template}\n")

    # 添加框架指导
    if style_config.framework:
        framework_info = FrameworkBuilder.build_framework_prompt(
            topic=topic,
            framework=style_config.framework,
            hook_type=style_config.hook_types[0] if style_config.hook_types else "curiosity",
        )
        parts.append(framework_info)

    # 添加风格特定的金句（如果有）
    if style_config.quotes:
        quote_theme = theme or list(style_config.quotes.keys())[0]
        quotes = style_config.quotes.get(quote_theme, [])
        if quotes:
            quote = random.choice(quotes)
            parts.append(f"【参考金句】\n「{quote}」\n")

    parts.append(f"【主题】\n{topic}")
    parts.append(f"【风格】\n{style_config.description}")

    parts.append("\n请生成 2-3 句视频文案（测试模式）。")

    return "\n\n".join(parts)


def _adapt_text_by_style(
    original_text: str,
    emotion: str,
    style_name: str,
    is_last_scene: bool,
    style_config,
) -> str:
    """根据风格适配文案"""
    adapted_text = original_text

    # 加缪风格需要特殊适配
    if style_name == "camus":
        ai_check = CamusStyleAdapter.detect_ai_flavor(original_text)
        poetic_check = CamusStyleAdapter.check_poetic_level(original_text)

        if ai_check["has_ai_flavor"] or not poetic_check["is_poetic"] or is_last_scene:
            adapted_text = CamusStyleAdapter.adapt_text(
                original_text,
                emotion=emotion,
                add_hook=is_last_scene,
                enhance_punc=True
            )
    # 其他风格也可以添加适配逻辑
    elif style_name in ("healing", "growth", "minimal"):
        # 为治愈、成长、极简风格添加emoji
        if style_config.use_emoji and style_config.emojis:
            emoji_emotion = emotion or list(style_config.emojis.keys())[0]
            emojis = style_config.emojis.get(emoji_emotion, [])
            if emojis and (len(original_text) * style_config.emoji_density < 1):
                # 根据密度决定是否添加emoji
                emoji = random.choice(emojis)
                adapted_text = f"{adapted_text} {emoji}"

        # 最后一句添加互动钩子
        if is_last_scene and style_config.ending_types:
            cta_type = random.choice(style_config.ending_types)
            if cta_type in ("question", "share", "follow"):
                cta = _get_cta_hook(cta_type)
                adapted_text = f"{adapted_text}\n{cta}"

    return adapted_text
