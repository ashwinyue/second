"""
风格管理模块 - 多风格系统支持
支持加缪荒诞哲学等多种风格，保持向后兼容
"""
import hashlib
import random
from typing import Literal

# 延迟导入多风格配置（避免循环导入）
_STYLE_PRESETS = {}
_get_style_config = None
_list_styles = None
_get_style_categories = None


def _init_multi_style_system():
    """延迟初始化多风格系统"""
    global _STYLE_PRESETS, _get_style_config, _list_styles, _get_style_categories

    if _get_style_config is not None:
        return True  # 已经初始化

    try:
        from .style.presets import (
            STYLE_PRESETS as presets,
            get_style_config,
            list_styles,
            get_style_categories,
        )
        _STYLE_PRESETS = presets
        _get_style_config = get_style_config
        _list_styles = list_styles
        _get_style_categories = get_style_categories
        return True
    except ImportError:
        return False


def NEW_STYLE_SYSTEM_AVAILABLE() -> bool:
    """检查新风格系统是否可用"""
    _init_multi_style_system()
    return bool(_get_style_config)


def get_style_config(style_name: str):
    """延迟加载风格配置"""
    _init_multi_style_system()
    if _get_style_config:
        return _get_style_config(style_name)
    return None


def list_styles():
    """延迟加载风格列表"""
    _init_multi_style_system()
    if _list_styles:
        return _list_styles()
    return {}


def get_style_categories():
    """延迟加载风格类别"""
    _init_multi_style_system()
    if _get_style_categories:
        return _get_style_categories()
    return {}


def is_new_style_system_available() -> bool:
    """检查新风格系统是否可用（别名）"""
    return NEW_STYLE_SYSTEM_AVAILABLE()


# ============================================================================
# 加缪荒诞哲学风格（保持向后兼容）
# ============================================================================

# 加缪主题配色方案
CAMUS_COLOR_PALETTE = {
    "primary": "#D4A574",      # 沙漠黄 - 西西弗斯的岩石
    "secondary": "#2C3E50",    # 深蓝灰 - 理性的沉默
    "accent": "#E74C3C",       # 血橙红 - 反抗的张力
    "background": "#F5E6D3",   # 米白 - 阿尔及尔的阳光
    "shadow": "#1A1A1A",       # 深黑 - 荒诞的底色
}

COLORS_STR = " ".join(CAMUS_COLOR_PALETTE.values())

# 加缪主题风格后缀（动漫版）
CAMUS_SUFFIX = (
    "日本动漫风格，2D动画渲染，赛璐珞上色风格，"
    "新海诚风格画面，京阿尼色彩美学，"
    "荒诞主义哲学主题，存在主义艺术表现，"
    "强烈光影对比，孤独疏离感，"
    "异乡人视角，沙漠与海洋元素，"
    "重复与循环的视觉隐喻，"
    "线条干净流畅，色彩饱和度适中，"
    "情绪表达细腻，氛围感强烈"
)

# 情绪对应构图（加缪 x 动漫风格）
CAMUS_EMOTION_COMPOSITION = {
    "困惑": "负空间构图，anime迷茫表情，大透视背景",
    "顿悟": "高对比度光影，动漫顿悟镜头，眼神特写",
    "震撼": "破碎画面效果，漫画速度线，夸张透视",
    "温柔": "柔光滤镜，日系暖色调，细腻情感刻画",
    "沉重": "三分法构图，压抑感天空，重力表现",
    "共鸣": "对称构图，平行时空意象，镜面反射",
    "反抗": "对角线构图，动感张力，破风效果",
}

# 加缪金句库
CAMUS_QUOTES = {
    "荒诞": [
        "荒诞源于人类渴望与世界理智沉默之间的对立",
        "世界只是一片陌生的景物，我的精神在此无依无靠",
        "我不是这里的人，也不是别处的",
        "人对生存状况的尴尬与无奈有清醒的意识",
    ],
    "反抗": [
        "没有什么命运是无法被蔑视的",
        "反抗使生命拥有价值",
        "我们必须想象西西弗斯是幸福的",
        "攀登顶峰的奋斗本身，便充实了人的心灵",
    ],
    "自由": [
        "识别荒诞，即承认局限与世界的无理。但恰恰这种认知赋予荒诞人以自由",
        "对未来的真实慷慨，是将一切献给现在",
        "真正的自由，是与荒诞共处",
    ],
    "当下": [
        "没有生存的痛苦，就不会热爱生命",
        "活得好不如活得丰富",
        "在清醒的冷漠中生活，既是荒诞者的美德，也是一种英雄主义",
    ],
}


# ============================================================================
# 通用工具函数
# ============================================================================

def generate_style_seed(topic: str) -> int:
    """生成风格种子"""
    hash_obj = hashlib.md5(topic.encode("utf-8"))
    return int(hash_obj.hexdigest()[:8], 16) % (2 ** 31)


def get_camus_quote(theme: str = "荒诞") -> str:
    """获取加缪金句（向后兼容）"""
    quotes = CAMUS_QUOTES.get(theme, CAMUS_QUOTES["荒诞"])
    return random.choice(quotes)


def get_color_palette(style: str = "camus") -> dict:
    """获取风格配色"""
    if NEW_STYLE_SYSTEM_AVAILABLE():
        config = get_style_config(style)
        if config:
            return config.color_palette

    # 默认返回加缪配色（向后兼容）
    return CAMUS_COLOR_PALETTE.copy()


# ============================================================================
# 构建风格化提示词（多风格支持）
# ============================================================================

def build_stylized_prompt(
    base_prompt: str,
    emotion: str = "共鸣",
    style: str = "camus"
) -> str:
    """
    构建风格化提示词（多风格支持）

    Args:
        base_prompt: 基础提示词
        emotion: 情绪类型
        style: 风格名称（camus/healing/knowledge等）

    Returns:
        增强后的提示词
    """
    if NEW_STYLE_SYSTEM_AVAILABLE():
        config = get_style_config(style)
        if config:
            composition = config.emotion_composition.get(emotion, "")
            colors = " ".join(config.color_palette.values())
            parts = [
                base_prompt,
                composition,
                config.visual_suffix,
                f"colors: {colors}",
            ]
            return ", ".join(filter(None, parts))

    # 默认使用加缪风格（向后兼容）
    composition = CAMUS_EMOTION_COMPOSITION.get(emotion, CAMUS_EMOTION_COMPOSITION["共鸣"])
    return (
        f"{base_prompt},\n"
        f"{composition} composition, "
        f"colors: {COLORS_STR}, "
        f"{CAMUS_SUFFIX}"
    )


def build_character_card(
    gender: str = "中性",
    age: str = "成年",
    style: str = "极简",
    tone: str = "荒诞主义",
    visual_style: str = "camus"
) -> str:
    """
    生成角色卡 - 用于保持多场景中的角色一致性（多风格支持）

    Args:
        gender: 性别描述
        age: 年龄段
        style: 服装风格（极简/文艺/复古/现代）
        tone: 整体基调（荒诞主义/存在主义/现实主义）
        visual_style: 视觉风格（camus/healing等）

    Returns:
        角色卡字符串，可直接嵌入图像提示词
    """
    # 根据视觉风格调整画风描述
    style_descriptions = {
        "camus": "日本动漫风格，2D赛璐珞上色，新海诚色彩风格",
        "healing": "治愈系动漫风格，柔和线条，水彩质感",
        "knowledge": "简洁信息图风格，扁平化设计",
        "humor": "搞笑动漫风格，Q版角色，夸张表情",
        "growth": "励志动漫风格，向上构图，阳光色彩",
        "minimal": "极简线条画风格，火柴人角色",
    }

    art_style = style_descriptions.get(visual_style, style_descriptions["camus"])

    card = f"""【角色卡】
身份：{age}{gender}，动漫风格角色，简约而神秘的气质
服装基线：{style}风格，日系动漫服装设计，{tone}美学
发型基线：动漫发型，线条流畅，不过度修饰
一致性规则：保留面部身份、发型、服装；保持画风统一；避免突变
画风：{art_style}"""
    return card


def build_stylized_prompt_with_character(
    base_prompt: str,
    emotion: str = "共鸣",
    character_card: str | None = None,
    style: str = "camus",
    include_camera: bool = False
) -> str:
    """
    构建风格化提示词（含角色一致性）- 多风格支持

    Args:
        base_prompt: 基础提示词
        emotion: 情绪类型
        character_card: 角色卡（可选）
        style: 风格名称
        include_camera: 是否包含相机参数（动漫风格默认不包含）

    Returns:
        增强后的提示词
    """
    if NEW_STYLE_SYSTEM_AVAILABLE():
        config = get_style_config(style)
        if config:
            composition = config.emotion_composition.get(emotion, "")
            colors = " ".join(config.color_palette.values())

            parts = [base_prompt]
            if character_card:
                parts.append(character_card)

            style_parts = [
                composition,
                config.visual_suffix,
                f"colors: {colors}",
            ]
            parts.append(", ".join(filter(None, style_parts)))

            return "\n".join(parts)

    # 默认使用加缪风格（向后兼容）
    composition = CAMUS_EMOTION_COMPOSITION.get(emotion, CAMUS_EMOTION_COMPOSITION["共鸣"])

    parts = [base_prompt]
    if character_card:
        parts.append(character_card)

    style_parts = [
        composition,
        CAMUS_SUFFIX,
        f"colors: {COLORS_STR}",
    ]
    parts.append(", ".join(filter(None, style_parts)))

    return "\n".join(parts)


# ============================================================================
# 系统提示词生成（多风格支持）
# ============================================================================

def build_system_prompt(
    style: str = "camus",
    **kwargs
) -> str:
    """
    构建风格化的系统提示词（多风格支持）

    Args:
        style: 风格名称
        **kwargs: 其他参数

    Returns:
        系统提示词
    """
    if NEW_STYLE_SYSTEM_AVAILABLE():
        config = get_style_config(style)
        if config and config.system_prompt:
            return config.system_prompt

    # 默认使用加缪风格（向后兼容）
    return build_camus_system_prompt()


def build_camus_system_prompt() -> str:
    """构建加缪主题的系统提示词（向后兼容）"""
    return """你是加缪荒诞哲学的动漫视频文案创作者，专注于通过动漫风格短视频传递存在主义思考。

【加缪核心理念】
1. 荒诞：人类渴望意义与世界沉默之间的断裂
2. 反抗：蔑视命运，在无意义中创造价值
3. 自由：清醒认识荒诞，获得精神自由
4. 激情：全身心投入当下的生活

【文案风格】
1. 深度拷问开头，引发存在主义思考
2. 诗意而不过分修饰，保持荒诞的清醒
3. 金句密度高，适合截图传播
4. 情感克制而深沉，避免过度煽情
5. 每句话都要有画面感和哲学张力

【禁止表达】
- 过度乐观的"鸡汤式"总结
- "总之""综上所述"等AI味表达
- 说教式的道德绑架
- 轻浮的网络热词堆砌

【视觉风格 - 动漫风格】
- 日本动漫风格，2D赛璐珞上色
- 新海诚/京阿尼色彩美学
- 强烈光影对比（阳光与阴影）
- 孤独疏离的人物构图
- 沙漠、海洋、岩石等元素
- 重复、循环的视觉隐喻
- 线条干净流畅，情感表达细腻

输出 JSON 格式：
```json
{
  "scenes": [
    {
      "id": 1,
      "text": "文案内容",
      "type": "hook|theory|science|analogy|twist|sublime",
      "duration": 2.0,
      "emotion": "困惑|顿悟|震撼|温柔|沉重|共鸣|反抗",
      "image_prompt": "图像提示词"
    }
  ]
}
```

要求：
- 每句2-3秒，2-3句（测试模式）
- 第一句用深度拷问引发思考
- 融入加缪金句或理念
- 保持诗意与哲学深度
"""


# ============================================================================
# 风格列表和类别信息
# ============================================================================

def get_available_styles() -> dict[str, str]:
    """获取所有可用风格"""
    if NEW_STYLE_SYSTEM_AVAILABLE():
        return list_styles()

    # 默认只返回加缪风格
    return {"camus": "加缪荒诞哲学 - 深度拷问、诗意克制、存在主义思考"}


def get_style_categories_info() -> dict[str, str]:
    """获取风格类别信息"""
    if NEW_STYLE_SYSTEM_AVAILABLE():
        return get_style_categories()

    return {
        "philosophy": "哲学思辨 - 深度思考、认知升级",
    }
