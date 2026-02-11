"""
多风格系统模块
支持加缪荒诞哲学、温暖治愈、硬核科普、幽默搞笑、成长觉醒、极简金句等多种风格
"""
# 直接导入 app.style_base 模块内容（避免循环导入）
import sys
from pathlib import Path

# 将项目根目录添加到路径
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 导入基础模块
import app.style_base as _base_style_module

# 从基础模块获取函数和变量
build_stylized_prompt = _base_style_module.build_stylized_prompt
generate_style_seed = _base_style_module.generate_style_seed
build_camus_system_prompt = _base_style_module.build_camus_system_prompt
get_camus_quote = _base_style_module.get_camus_quote
get_color_palette = _base_style_module.get_color_palette
build_character_card = _base_style_module.build_character_card
build_stylized_prompt_with_character = _base_style_module.build_stylized_prompt_with_character
build_system_prompt = _base_style_module.build_system_prompt
get_available_styles = _base_style_module.get_available_styles
get_style_categories_info = _base_style_module.get_style_categories_info

# 加缪主题配色和风格
CAMUS_COLOR_PALETTE = _base_style_module.CAMUS_COLOR_PALETTE
CAMUS_SUFFIX = _base_style_module.CAMUS_SUFFIX
CAMUS_EMOTION_COMPOSITION = _base_style_module.CAMUS_EMOTION_COMPOSITION
CAMUS_QUOTES = _base_style_module.CAMUS_QUOTES

# 向后兼容的别名
MINIMALIST_SUFFIX = CAMUS_SUFFIX
COLOR_PALETTE = CAMUS_COLOR_PALETTE
COLORS_STR = " ".join(CAMUS_COLOR_PALETTE.values())
EMOTION_COMPOSITION = CAMUS_EMOTION_COMPOSITION

# 加缪语感适配器模块导出
from .xiaohongshu import (
    CamusStyleAdapter,
    CAMUS_STYLE_MODIFIER,
    detect_and_adapt_camus,
)

# 加缪模板库模块导出
from .templates import (
    build_camus_opening_prompt,
    CamusEndingGenerator,
    CamusTemplateGenerator,
    get_camus_quote as get_quote_from_templates,
    get_camus_emoji,
    get_all_opening_types,
    CAMUS_OPENING_TEMPLATES,
    CAMUS_ENDING_TRIAD,
    CAMUS_QUOTES as TEMPLATE_QUOTES,
    CAMUS_EMOJI as TEMPLATE_EMOJI,
)

# 多风格框架导出
from .frameworks import (
    GOLDEN_3S_HOOKS,
    EMOTIONAL_HOOKS,
    COPY_FRAMEWORKS,
    CTA_HOOKS,
    RHYTHM_PATTERNS,
    CopyAnalyzer,
    FrameworkBuilder,
    get_available_hooks,
    get_available_frameworks,
    get_available_emotions,
)

# 多风格预设导出
from .presets import (
    StyleConfig,
    STYLE_PRESETS,
    CAMUS_CONFIG,
    HEALING_CONFIG,
    KNOWLEDGE_CONFIG,
    HUMOR_CONFIG,
    GROWTH_CONFIG,
    MINIMAL_CONFIG,
    get_style_config,
    list_styles,
    list_styles_by_category,
    get_default_style,
    get_style_categories,
)

__all__ = [
    # ========== 基础函数导出 ==========
    "build_stylized_prompt",
    "generate_style_seed",
    "build_camus_system_prompt",
    "build_system_prompt",
    "get_camus_quote",
    "get_color_palette",
    "build_character_card",
    "build_stylized_prompt_with_character",
    "get_available_styles",
    "get_style_categories_info",

    # ========== 加缪主题配色和风格 ==========
    "CAMUS_COLOR_PALETTE",
    "CAMUS_SUFFIX",
    "CAMUS_EMOTION_COMPOSITION",
    "CAMUS_QUOTES",

    # ========== 向后兼容别名 ==========
    "MINIMALIST_SUFFIX",
    "COLOR_PALETTE",
    "COLORS_STR",
    "EMOTION_COMPOSITION",

    # ========== 语感适配器导出 ==========
    "CamusStyleAdapter",
    "CAMUS_STYLE_MODIFIER",
    "detect_and_adapt_camus",

    # ========== 模板库导出 ==========
    "build_camus_opening_prompt",
    "CamusEndingGenerator",
    "CamusTemplateGenerator",
    "get_camus_emoji",
    "get_all_opening_types",
    "CAMUS_OPENING_TEMPLATES",
    "CAMUS_ENDING_TRIAD",

    # ========== 文案框架导出 ==========
    "GOLDEN_3S_HOOKS",
    "EMOTIONAL_HOOKS",
    "COPY_FRAMEWORKS",
    "CTA_HOOKS",
    "RHYTHM_PATTERNS",
    "CopyAnalyzer",
    "FrameworkBuilder",
    "get_available_hooks",
    "get_available_frameworks",
    "get_available_emotions",

    # ========== 风格预设导出 ==========
    "StyleConfig",
    "STYLE_PRESETS",
    "CAMUS_CONFIG",
    "HEALING_CONFIG",
    "KNOWLEDGE_CONFIG",
    "HUMOR_CONFIG",
    "GROWTH_CONFIG",
    "MINIMAL_CONFIG",
    "get_style_config",
    "list_styles",
    "list_styles_by_category",
    "get_default_style",
    "get_style_categories",
]
