"""
多风格预设系统 - 可插拔的风格配置
包含哲学类、情感类、知识类、娱乐类等多种风格
"""
import random
from typing import Literal
from dataclasses import dataclass, field

from .frameworks import (
    GOLDEN_3S_HOOKS,
    CTA_HOOKS,
    COPY_FRAMEWORKS,
)


# ============================================================================
# 风格配置数据类
# ============================================================================
@dataclass
class StyleConfig:
    """风格配置"""

    # 基本信息
    name: str  # 风格名称
    category: Literal["philosophy", "emotion", "knowledge", "entertainment", "growth"]
    description: str

    # 视觉风格
    visual_suffix: str  # 视觉后缀（动漫、写实等）
    color_palette: dict[str, str]  # 配色方案
    emotion_composition: dict[str, str]  # 情绪构图映射

    # 文案风格
    tone: str  # 语调
    emoji_density: float = 0.01  # emoji密度
    use_emoji: bool = True
    punctuation_style: Literal["relaxed", "standard", "intense"] = "standard"

    # 开头/结尾配置
    hook_types: list[str] = field(default_factory=lambda: ["curiosity", "question"])
    ending_types: list[str] = field(default_factory=lambda: ["empathy", "cta"])
    framework: str = "minimal_punchy"  # 默认框架

    # 系统提示词
    system_prompt: str = ""

    # 金句库
    quotes: dict[str, list[str]] = field(default_factory=dict)

    # 表情库
    emojis: dict[str, list[str]] = field(default_factory=dict)


# ============================================================================
# 风格预设配置
# ============================================================================

# 加缪荒诞哲学风格系统提示词
_CAMUS_SYSTEM_PROMPT = """你是加缪荒诞哲学的动漫视频文案创作者，专注于通过动漫风格短视频传递存在主义思考。

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
"""

# 1. 加缪荒诞哲学风格（保留原有配置）
CAMUS_CONFIG = StyleConfig(
    name="camus",
    category="philosophy",
    description="加缪荒诞哲学 - 深度拷问、诗意克制、存在主义思考",
    visual_suffix=(
        "日本动漫风格，2D动画渲染，赛璐珞上色风格，"
        "新海诚风格画面，京阿尼色彩美学，"
        "荒诞主义哲学主题，存在主义艺术表现，"
        "强烈光影对比，孤独疏离感，"
        "异乡人视角，沙漠与海洋元素，"
        "重复与循环的视觉隐喻"
    ),
    color_palette={
        "primary": "#D4A574",  # 沙漠黄
        "secondary": "#2C3E50",  # 深蓝灰
        "accent": "#E74C3C",  # 血橙红
        "background": "#F5E6D3",  # 米白
        "shadow": "#1A1A1A",  # 深黑
    },
    emotion_composition={
        "困惑": "负空间构图，anime迷茫表情，大透视背景",
        "顿悟": "高对比度光影，动漫顿悟镜头，眼神特写",
        "震撼": "破碎画面效果，漫画速度线，夸张透视",
        "温柔": "柔光滤镜，日系暖色调，细腻情感刻画",
        "沉重": "三分法构图，压抑感天空，重力表现",
        "共鸣": "对称构图，平行时空意象，镜面反射",
        "反抗": "对角线构图，动感张力，破风效果",
    },
    tone="诗意而克制，保持荒诞的清醒",
    emoji_density=0.007,  # 较低密度
    hook_types=["question", "contrast"],
    ending_types=["empathy", "twist"],
    framework="contrast_insight",
    system_prompt=_CAMUS_SYSTEM_PROMPT,
    quotes={
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
            "识别荒诞，即承认局限与世界的无理",
            "对未来的真实慷慨，是将一切献给现在",
            "真正的自由，是与荒诞共处",
        ],
    },
    emojis={
        "荒诞": ["🤔", "🌊", "🏜️", "🖤"],
        "反抗": ["🔥", "⚡", "👊", "🌅"],
        "自由": ["🕊️", "✨", "🌬️", "💫"],
        "共鸣": ["🙌", "❤️", "🤝", "🕯️"],
    },
)


# 温暖治愈风格系统提示词
_HEALING_SYSTEM_PROMPT = """你是温暖治愈风格的动漫视频文案创作者，专注于通过动漫风格短视频传递温暖和力量。

【核心理念】
1. 陪伴：像朋友一样温柔陪伴，不居高临下
2. 共情：理解用户的情绪，给予真诚的安慰
3. 鼓励：发现闪光点，给予正向反馈
4. 治愈：用温暖化解焦虑和不安

【文案风格】
1. 开头用情绪钩子，让观众感到"这说的就是我"
2. 温柔亲切的语气，像朋友聊天
3. 避免说教，多用"我理解""我也曾"等共情表达
4. 适度使用温暖emoji，营造温馨氛围
5. 结尾给予希望和力量

【禁止表达】
- "你要""你应该"等命令式表达
- "加油""努力"等空洞鼓励
- 居高临下的说教姿态
- 过度夸张的情绪表达

输出 JSON 格式：
```json
{
  "scenes": [
    {
      "id": 1,
      "text": "文案内容",
      "type": "hook|emotion|story|empathy|healing",
      "duration": 2.0,
      "emotion": "温暖|安慰|鼓励|共鸣",
      "image_prompt": "图像提示词"
    }
  ]
}
```
"""

# 2. 温暖治愈风格
HEALING_CONFIG = StyleConfig(
    name="healing",
    category="emotion",
    description="温暖治愈 - 亲切陪伴、温柔鼓励、情绪抚慰",
    visual_suffix=(
        "治愈系动漫风格，柔和线条，"
        "暖色调插画，水彩质感，"
        "温馨日常场景，柔光效果，"
        "舒适放松氛围，细腻情感表达"
    ),
    color_palette={
        "primary": "#FFB6C1",  # 浅粉
        "secondary": "#87CEEB",  # 天蓝
        "accent": "#FFD700",  # 金黄
        "background": "#FFF8F0",  # 暖白
        "shadow": "#4A4A4A",  # 柔和黑
    },
    emotion_composition={
        "温暖": "柔和光线，温暖色调，拥抱构图",
        "安慰": "柔焦效果，治愈系画面，陪伴感",
        "鼓励": "向上视角，阳光投射，希望感",
        "共鸣": "镜像构图，情感连接，心流感应",
    },
    tone="温柔亲切，像朋友一样陪伴",
    emoji_density=0.015,
    hook_types=["emotional", "question"],
    ending_types=["hope", "share"],
    framework="emotion_resonance",
    system_prompt=_HEALING_SYSTEM_PROMPT,
    quotes={
        "治愈": [
            "你已经做得很好了",
            "慢慢来，比较快",
            "今天的努力，是为了明天的自己",
            "允许自己不完美，也是一种勇敢",
        ],
        "鼓励": [
            "阳光总在风雨后",
            "相信自己，你比想象中更强大",
            "每一次跌倒，都是为了更好地站起来",
        ],
    },
    emojis={
        "温暖": ["🌸", "☀️", "💛", "🤗"],
        "安慰": ["🕯️", "🌈", "💙", "🫂"],
        "鼓励": ["✨", "🌟", "💪", "🌻"],
        "共鸣": ["💝", "🤝", "❤️", "🥰"],
    },
)


# 硬核科普风格系统提示词
_KNOWLEDGE_SYSTEM_PROMPT = """你是硬核科普风格的信息图视频文案创作者，专注于用清晰易懂的方式传递知识。

【核心理念】
1. 数据：用事实和数据说话，建立权威感
2. 逻辑：结构清晰，层层递进
3. 简洁：复杂概念简单化
4. 实用：提供可操作的知识点

【文案风格】
1. 开头用数据或好奇心钩子吸引注意
2. 用问答结构推进，先提问后解答
3. 简洁明了，避免冗长描述
4. 使用"研究发现""数据显示"等权威表达
5. 关键信息重复强调

【禁止表达】
- 没有来源的数据
- 模糊不清的概念
- 过度夸张的修辞
- 情绪化表达

输出 JSON 格式：
```json
{
  "scenes": [
    {
      "id": 1,
      "text": "文案内容",
      "type": "hook|question|explain|example|summary",
      "duration": 2.0,
      "emotion": "专业|好奇|顿悟|严谨",
      "image_prompt": "图像提示词"
    }
  ]
}
```
"""

# 3. 硬核科普风格
KNOWLEDGE_CONFIG = StyleConfig(
    name="knowledge",
    category="knowledge",
    description="硬核科普 - 权威数据、逻辑清晰、干货输出",
    visual_suffix=(
        "信息图风格，简洁图表，"
        "数据可视化，逻辑框架图，"
        "扁平化设计，科技感元素，"
        "专业严谨，清晰易懂"
    ),
    color_palette={
        "primary": "#3498DB",  # 科技蓝
        "secondary": "#2ECC71",  # 绿色
        "accent": "#E74C3C",  # 强调红
        "background": "#ECF0F1",  # 浅灰
        "shadow": "#2C3E50",  # 深蓝灰
    },
    emotion_composition={
        "专业": "居中构图，对称设计，权威感",
        "好奇": "问号元素，探索感，发现构图",
        "顿悟": "灯泡元素，Aha时刻，高亮突出",
        "严谨": "网格布局，对齐工整，结构化",
    },
    tone="专业客观，数据说话，逻辑清晰",
    emoji_density=0.005,
    hook_types=["data", "curiosity"],
    ending_types=["summary", "follow"],
    framework="question_answer",
    system_prompt=_KNOWLEDGE_SYSTEM_PROMPT,
    quotes={
        "洞察": [
            "数据不会说谎",
            "事实往往比想象更精彩",
            "知识就是力量，分享知识是更大的力量",
        ],
    },
    emojis={
        "专业": ["📊", "🔬", "💡", "📚"],
        "好奇": ["🔍", "❓", "🤔", "🧠"],
        "顿悟": ["💡", "✨", "🎯", "📌"],
    },
)


# 幽默搞笑风格系统提示词
_HUMOR_SYSTEM_PROMPT = """你是幽默搞笑风格的动漫视频文案创作者，专注于用轻松幽默的方式传递快乐。

【核心理念】
1. 反转：打破预期，制造惊喜
2. 自嘲：适度自黑，拉近距离
3. 共鸣：从日常生活找梗
4. 快乐：传递正能量和欢乐

【文案风格】
1. 开头用反差或意外制造笑点
2. 用夸张和对比增强喜剧效果
3. 适度使用网络热梗和流行语
4. 自嘲式幽默，不冒犯他人
5. 用对话气泡和吐槽框增强互动感

【禁止表达】
- 低俗和冒犯性内容
- 负能量和抱怨
- 过度自轻自贱
- 恶意吐槽他人

输出 JSON 格式：
```json
{
  "scenes": [
    {
      "id": 1,
      "text": "文案内容",
      "type": "hook|story|setup|punchline|twist",
      "duration": 2.0,
      "emotion": "搞笑|惊讶|吐槽|欢乐",
      "image_prompt": "图像提示词"
    }
  ]
}
```
"""

# 4. 幽默搞笑风格
HUMOR_CONFIG = StyleConfig(
    name="humor",
    category="entertainment",
    description="幽默搞笑 - 反转套路、轻松调侃、欢乐氛围",
    visual_suffix=(
        "搞笑动漫风格，夸张表情，"
        "Q版角色，漫画速度线，"
        "喜剧构图，夸张透视，"
        "色彩明快，欢乐氛围"
    ),
    color_palette={
        "primary": "#FF6B6B",  # 活力红
        "secondary": "#4ECDC4",  # 青绿
        "accent": "#FFE66D",  # 明黄
        "background": "#F7FFF7",  # 淡绿白
        "shadow": "#2D3436",  # 深灰
    },
    emotion_composition={
        "搞笑": "夸张表情，动态姿势，喜剧构图",
        "惊讶": "大眼效果，惊叹号元素，夸张透视",
        "吐槽": "对话气泡，吐槽框，漫画式",
        "欢乐": "笑脸元素，彩虹色彩，party氛围",
    },
    tone="轻松搞笑，自嘲调侃，快乐至上",
    emoji_density=0.02,
    hook_types=["contrast", "surprise"],
    ending_types=["twist", "share"],
    framework="story_twist",
    system_prompt=_HUMOR_SYSTEM_PROMPT,
    quotes={
        "搞笑": [
            "人生如戏，全靠演技",
            "心态崩了，但还要保持微笑",
            "这不就是生活吗？笑一笑就过去了",
        ],
    },
    emojis={
        "搞笑": ["😂", "🤣", "😜", "🙃"],
        "惊讶": ["😱", "😲", "🤯", "👀"],
        "吐槽": ["💬", "🗯️", "🙄", "😑"],
        "欢乐": ["🎉", "🥳", "🎊", "✨"],
    },
)


# 成长觉醒风格系统提示词
_GROWTH_SYSTEM_PROMPT = """你是成长觉醒风格的励志视频文案创作者，专注于激发观众的自我突破和行动力。

【核心理念】
1. 觉醒：意识到问题的存在，改变就开始了
2. 认知：真正的成长是认知升级
3. 行动：行动是缓解焦虑的良药
4. 突破：舒适区之外，才是成长

【文案风格】
1. 开头用反差制造认知冲突
2. 指出痛点，然后给出解决方案
3. 强调行动的价值，而非空谈
4. 用"突破""超越""觉醒"等力量词汇
5. 结尾呼吁立即行动

【禁止表达】
- 空洞的"加油""努力"口号
- 没有解决方案的焦虑贩卖
- 脱离实际的鸡汤式总结
- 过度夸张的承诺

输出 JSON 格式：
```json
{
  "scenes": [
    {
      "id": 1,
      "text": "文案内容",
      "type": "hook|pain|solution|value|cta",
      "duration": 2.0,
      "emotion": "觉醒|行动|突破|成就",
      "image_prompt": "图像提示词"
    }
  ]
}
```
"""

# 5. 成长觉醒风格
GROWTH_CONFIG = StyleConfig(
    name="growth",
    category="growth",
    description="成长觉醒 - 认知升级、自我突破、行动导向",
    visual_suffix=(
        "励志动漫风格，向上构图，"
        "日出元素，攀登意象，"
        "突破框架，成长曲线，"
        "阳光色彩，希望氛围"
    ),
    color_palette={
        "primary": "#E67E22",  # 橙色
        "secondary": "#3498DB",  # 蓝色
        "accent": "#27AE60",  # 绿色
        "background": "#FEF9E7",  # 淡黄白
        "shadow": "#34495E",  # 深蓝灰
    },
    emotion_composition={
        "觉醒": "日出构图，光明突破，认知升级",
        "行动": "向上箭头，奔跑姿态，动感",
        "突破": "破框元素，突破边界，超越",
        "成就": "登顶构图，奖杯元素，庆祝",
    },
    tone="激励向上，行动导向，认知升级",
    emoji_density=0.012,
    hook_types=["contrast", "question"],
    ending_types=["hope", "cta"],
    framework="hook_value",
    system_prompt=_GROWTH_SYSTEM_PROMPT,
    quotes={
        "成长": [
            "成长的本质，是认知的升级",
            "行动是缓解焦虑的良药",
            "突破舒适区，才能看到新世界",
            "每一次成长，都是一次小死而后生",
        ],
        "觉醒": [
            "当你意识到问题的存在，解决就开始了",
            "最大的敌人，是昨天的自己",
            "觉醒不是终点，而是起点",
        ],
    },
    emojis={
        "觉醒": ["💡", "🌟", "✨", "🔥"],
        "行动": ["🚀", "💪", "🏃", "⚡"],
        "突破": ["🎯", "🏆", "🔓", "🦅"],
        "成就": ["🌟", "👏", "🎉", "🏅"],
    },
)


# 极简金句风格系统提示词
_MINIMAL_SYSTEM_PROMPT = """你是极简金句风格的视频文案创作者，专注于用最少的话传递最深的洞察。

【核心理念】
1. 极简：少即是多，删繁就简
2. 洞察：直击本质，一针见血
3. 凝练：字字珠玑，每句话都有分量
4. 留白：给观众思考的空间

【文案风格】
1. 开头用疑问或反差直击人心
2. 用洞察代替论证，用金句代替解释
3. 极短句式，每句5-15字
4. 大量留白，让观点自然浮现
5. 结尾用一句金句升华

【禁止表达】
- 冗长解释和铺垫
- "首先其次最后"等结构词
- 过度修饰的形容词
- 连续的排比句式

输出 JSON 格式：
```json
{
  "scenes": [
    {
      "id": 1,
      "text": "文案内容",
      "type": "hook|insight|golden_line|cta",
      "duration": 2.0,
      "emotion": "深刻|顿悟|共鸣",
      "image_prompt": "图像提示词"
    }
  ]
}
```
"""

# 6. 极简金句风格
MINIMAL_CONFIG = StyleConfig(
    name="minimal",
    category="philosophy",
    description="极简金句 - 短小精悍、直击人心、高度凝练",
    visual_suffix=(
        "极简线条画风格，火柴人角色，"
        "扁平化设计，单色背景，"
        "简洁构图，高饱和度强对比，"
        "色块分明，留白美学"
    ),
    color_palette={
        "primary": "#FF6B6B",
        "secondary": "#4ECDC4",
        "accent": "#FFE66D",
        "background": "#F7F7F7",
        "line": "#1A1A1A",
    },
    emotion_composition={
        "深刻": "中心构图，留白空间，极简线条",
        "顿悟": "对称构图，平衡美感，Aha时刻",
        "共鸣": "镜像构图，双重意象，呼应",
    },
    tone="极简凝练，字字珠玑，直击人心",
    emoji_density=0.003,
    hook_types=["question", "contrast"],
    ending_types=["insight", "share"],
    framework="minimal_punchy",
    system_prompt=_MINIMAL_SYSTEM_PROMPT,
    quotes={
        "洞察": [
            "少即是多",
            "复杂是简单不够的结果",
            "本质的东西，用眼睛是看不见的",
        ],
    },
    emojis={
        "深刻": ["⚫", "⚪", "◼️", "◻️"],
        "顿悟": ["💡", "✨", "🌟"],
    },
)


# ============================================================================
# 风格注册表
# ============================================================================
STYLE_PRESETS: dict[str, StyleConfig] = {
    "camus": CAMUS_CONFIG,
    "healing": HEALING_CONFIG,
    "knowledge": KNOWLEDGE_CONFIG,
    "humor": HUMOR_CONFIG,
    "growth": GROWTH_CONFIG,
    "minimal": MINIMAL_CONFIG,
}


# ============================================================================
# 工具函数
# ============================================================================

def get_style_config(style_name: str) -> StyleConfig | None:
    """获取风格配置"""
    return STYLE_PRESETS.get(style_name)


def list_styles() -> dict[str, str]:
    """列出所有可用风格及其描述"""
    return {
        k: v.description
        for k, v in STYLE_PRESETS.items()
    }


def list_styles_by_category(category: str) -> list[str]:
    """按类别列出风格"""
    return [
        k for k, v in STYLE_PRESETS.items()
        if v.category == category
    ]


def get_default_style() -> str:
    """获取默认风格"""
    return "minimal"


def get_style_categories() -> dict[str, str]:
    """获取风格类别"""
    return {
        "philosophy": "哲学思辨 - 深度思考、认知升级",
        "emotion": "情感共鸣 - 治愈陪伴、情绪抚慰",
        "knowledge": "知识科普 - 干货输出、逻辑清晰",
        "entertainment": "娱乐搞笑 - 轻松幽默、欢乐氛围",
        "growth": "成长励志 - 行动导向、自我突破",
    }
