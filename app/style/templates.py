"""
加缪荒诞哲学模板库
专注于深度拷问式开头和存在主义金句结尾
"""
import random
from typing import Literal


# ========== 加缪主题：深度拷问开头模板 ==========
CAMUS_OPENING_TEMPLATES = {
    # ========== 荒诞拷问 ==========
    "absurd": {
        "description": "用荒诞感引发存在主义思考",
        "templates": [
            "你有没有过一种感觉，明明{正常状态}，却{异常感受}？",
            "为什么{现象}，我们却{反常反应}？",
            "日复一日重复的生活，难道不是{荒诞隐喻}吗？",
            "你以为{认知}，其实{真相}！",
        ],
        "examples": [
            "你有没有过一种感觉，明明活着，却找不到意义？",
            "为什么越努力越空虚？真相扎心了",
            "日复一日重复的生活，难道不是另一种形式的西西弗斯吗？",
            "你以为的迷茫，其实是荒诞的开始...",
        ]
    },

    # ========== 存在拷问 ==========
    "existence": {
        "description": "直击生存本质的终极追问",
        "templates": [
            "如果{假设条件}，你还会{行动}吗？",
            "唯一真正{严肃程度}的问题是{终极问题}",
            "当{条件}时，你{如何选择}？",
            "{终极问题}，你思考过吗？",
        ],
        "examples": [
            "如果生命没有意义，你还会努力活着吗？",
            "唯一真正严肃的哲学问题便是自杀",
            "当上帝已死，你的信仰还剩下什么？",
            "死亡终至，这期间我们该如何活着？",
        ]
    },

    # ========== 反抗拷问 ==========
    "rebellion": {
        "description": "从荒诞中寻找反抗的力量",
        "templates": [
            "面对{困境}，我们只能{绝望}吗？",
            "{现象}不可怕，可怕的是{深层问题}",
            "为什么{正常现象}，我却{觉醒感受}？",
            "感谢{挫折}，让我{成长/顿悟}",
        ],
        "examples": [
            "面对荒诞，我们只能绝望吗？",
            "痛苦不可怕，可怕的是失去感受的能力",
            "为什么同样的生活，我却活得如此疲惫？",
            "感谢那次崩溃，让我重新认识自己",
        ]
    },
}


# ========== 加缪主题：结尾三件套 ==========
CAMUS_ENDING_TRIAD = {
    # 共情金句 - 加缪风格
    "empathy": [
        "我们必须想象{主体}是{状态}",
        "真正的{价值}，是{定义}",
        "有时候{反直觉}，反而{正面结果}",
        "人生最大的{名词}，就是{意外转折}",
        "{行动}本身，便充实了{对象}",
    ],

    # 反转结尾 - 从荒诞到反抗
    "twist": [
        "谢谢{挫折}，让我学会了{成长}",
        "{预期结果}？不，{反转结局}",
        "后来才发现，{表面现象}其实是{真相}",
        "{初始困境}，最后成了{意外礼物}",
        "原来{概念}如此简单，我们却想了{程度}",
    ],

    # 互动钩子 - 哲学共鸣
    "interaction": [
        "你有过{场景}吗？留言区说说👇",
        "如果{假设}，你会{选择}？",
        "这说的是不是你？",
        "你觉得{观点}对吗？来辩～",
        "认同的{称呼}点个赞{emoji}",
    ],
}


# ========== 加缪金句库（可直接嵌入文案）==========
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
        "识别荒诞，即承认局限与世界的无理",
        "对未来的真实慷慨，是将一切献给现在",
        "真正的自由，是与荒诞共处",
    ],
    "当下": [
        "没有生存的痛苦，就不会热爱生命",
        "活得好不如活得丰富",
        "在清醒的冷漠中生活，既是荒诞者的美德",
    ],
}


# ========== 加缪主题表情库 ==========
CAMUS_EMOJI = {
    "荒诞": ["🤔", "🌊", "🏜️", "🖤"],
    "反抗": ["🔥", "⚡", "👊", "🌅"],
    "自由": ["🕊️", "✨", "🌬️", "💫"],
    "共鸣": ["🙌", "❤️", "🤝", "🕯️"],
}


# ========== 模板生成器 ==========
class CamusTemplateGenerator:
    """加缪主题模板生成器"""

    @staticmethod
    def get_opening_type() -> Literal["absurd", "existence", "rebellion"]:
        """随机获取一个开头类型"""
        return random.choice(list(CAMUS_OPENING_TEMPLATES.keys()))

    @staticmethod
    def generate_opening(
        opening_type: str,
        **kwargs
    ) -> str:
        """
        生成加缪风格的开头

        Args:
            opening_type: 开头类型（absurd/existence/rebellion）
            **kwargs: 填充变量

        Returns:
            生成的开头文案
        """
        if opening_type not in CAMUS_OPENING_TEMPLATES:
            opening_type = "absurd"

        config = CAMUS_OPENING_TEMPLATES[opening_type]
        templates = config["templates"]

        # 随机选择模板并填充
        template = random.choice(templates)
        return template.format(**kwargs)

    @staticmethod
    def get_example_opening(theme: str = "荒诞") -> str:
        """
        获取预设示例开头

        Args:
            theme: 主题（荒诞/反抗/自由）

        Returns:
            示例开头
        """
        if theme == "荒诞":
            return random.choice(CAMUS_OPENING_TEMPLATES["absurd"]["examples"])
        elif theme == "反抗":
            return random.choice(CAMUS_OPENING_TEMPLATES["rebellion"]["examples"])
        else:
            return random.choice(CAMUS_OPENING_TEMPLATES["existence"]["examples"])

    @staticmethod
    def get_quote(theme: str = "荒诞") -> str:
        """获取加缪金句"""
        return random.choice(CAMUS_QUOTES.get(theme, CAMUS_QUOTES["荒诞"]))

    @staticmethod
    def get_emoji(emotion: str = "共鸣") -> str:
        """获取主题对应的emoji"""
        emojis = CAMUS_EMOJI.get(emotion, CAMUS_EMOJI["共鸣"])
        return random.choice(emojis)


# ========== 结尾生成器 ==========
class CamusEndingGenerator:
    """加缪主题结尾生成器"""

    @staticmethod
    def generate_empathy(**kwargs) -> str:
        """生成共情金句"""
        template = random.choice(CAMUS_ENDING_TRIAD["empathy"])
        return template.format(**kwargs)

    @staticmethod
    def generate_twist(**kwargs) -> str:
        """生成反转结尾"""
        template = random.choice(CAMUS_ENDING_TRIAD["twist"])
        return template.format(**kwargs)

    @staticmethod
    def generate_interaction(**kwargs) -> str:
        """生成互动钩子"""
        template = random.choice(CAMUS_ENDING_TRIAD["interaction"])
        return template.format(**kwargs)

    @staticmethod
    def generate_full_ending(**kwargs) -> str:
        """生成完整的结尾三件套"""
        parts = []

        # 共情金句
        empathy = CamusEndingGenerator.generate_empathy(**kwargs)
        parts.append(empathy)

        # 反转结尾
        twist = CamusEndingGenerator.generate_twist(**kwargs)
        parts.append(twist)

        # 互动钩子
        interaction = CamusEndingGenerator.generate_interaction(**kwargs)
        parts.append(interaction)

        return "\n".join(parts)


# ========== Prompt 构建器 ==========
def build_camus_opening_prompt(
    topic: str,
    theme: str = "荒诞"
) -> str:
    """
    构建加缪风格的开头提示

    Args:
        topic: 主题
        theme: 主题类型（荒诞/反抗/自由）

    Returns:
        增强后的提示词
    """
    # 获取示例
    example = CamusTemplateGenerator.get_example_opening(theme)

    return f"""【开头要求：深度拷问】
用存在主义的方式引发思考，避免AI味和说教感。

参考示例：
- {example}

主题：{topic}
风格：加缪荒诞哲学

要求：
1. 第一句必须引发存在主义思考
2. 使用"你有没有""为什么""如果"等拷问句式
3. 制造荒诞感或反差
4. 保持诗意，避免过度煽情
"""


# ========== 导出便捷函数 ==========
def get_camus_quote(theme: str = "荒诞") -> str:
    """获取加缪金句"""
    return CamusTemplateGenerator.get_quote(theme)


def get_camus_emoji(emotion: str = "共鸣") -> str:
    """获取加缪主题emoji"""
    return CamusTemplateGenerator.get_emoji(emotion)


def get_all_opening_types() -> dict:
    """获取所有开头类型的描述"""
    return {
        key: value["description"]
        for key, value in CAMUS_OPENING_TEMPLATES.items()
    }
