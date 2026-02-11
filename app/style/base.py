"""
基础风格模块（从 app/style.py 迁移）
"""
import hashlib


# 极简风格配置
MINIMALIST_SUFFIX = (
    "极简线条画风格，火柴人角色四肢为黑色线条，"
    "扁平化设计，单色背景，简洁构图，"
    "高饱和度强对比色块分明"
)

COLOR_PALETTE = {
    "primary": "#FF6B6B",
    "secondary": "#4ECDC4",
    "accent": "#FFE66D",
    "background": "#F7F7F7",
    "line": "#1A1A1A",
}

COLORS_STR = " ".join(COLOR_PALETTE.values())

# 情绪对应构图
EMOTION_COMPOSITION = {
    "困惑": "diagonal",
    "顿悟": "center symmetry",
    "震撼": "frame",
    "温柔": "negative space",
    "沉重": "rule of thirds",
    "共鸣": "center symmetry",
}


def generate_style_seed(topic: str) -> int:
    """生成风格种子"""
    hash_obj = hashlib.md5(topic.encode("utf-8"))
    return int(hash_obj.hexdigest()[:8], 16) % (2 ** 31)


def build_stylized_prompt(base_prompt: str, emotion: str = "中性") -> str:
    """构建风格化提示词"""
    composition = EMOTION_COMPOSITION.get(emotion, "center symmetry")

    return (
        f"{base_prompt},\n"
        f"{composition} composition, "
        f"colors: {COLORS_STR}, "
        f"{MINIMALIST_SUFFIX}"
    )
