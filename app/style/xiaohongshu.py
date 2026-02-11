"""
加缪荒诞哲学语感适配器
实现AI味检测、诗意化检测、存在主义风格适配
"""
import re
import random
from typing import Literal


# ========== 加缪语感强制规则 ==========
CAMUS_STYLE_MODIFIER = """
【加缪语感强制规则】
1. 诗意克制：避免过度修饰，保持荒诞的清醒
2. 标点符号：克制使用感叹号，多用句号和省略号
3. Emoji密度：每150字1个，选择存在主义符号
4. 称呼体系：避免"姐妹们"等轻浮称呼，使用"朋友"或直接开始
5. 互动钩子：哲学式追问，而非"打在评论区"
6. 标题结构：存在主义拷问 + 金句总结
"""


# ========== AI味检测词库 ==========
AI_FLAVOR_WORDS = [
    "综上所述", "由此可见", "值得注意的是", "首先...其次...最后",
    "一方面...另一方面", "换言之", "换句话说", "也就是说",
    "显而易见", "毫无疑问", "总的来说", "总而言之",
    "让我们", "我们需要", "不容忽视", "毋庸置疑"
]


# ========== 过度煽情检测 ==========
OVERLY_EMOTIONAL_PATTERNS = [
    r"[！]{2,}",  # 连续感叹号
    r"[~～]{2,}",  # 连续波浪号
    r"[呀咪嗷哇]{2,}",  # 娇嗔语气词
]


# ========== 加缪主题表情库 ==========
CAMUS_EMOJI = {
    "困惑": ["🤔", "🌊", "🖤"],
    "顿悟": ["💡", "✨", "🌅"],
    "震撼": ["⚡", "🔥", "👊"],
    "温柔": ["🕯️", "🌬️", "☁️"],
    "沉重": ["🎭", "🏜️", "🌧️"],
    "共鸣": ["🤝", "🙌", "❤️"],
    "反抗": ["🔥", "⚡", "🌅"],
}


# ========== 存在主义互动钩子 ==========
EXISTENTIAL_HOOKS = [
    "你有过这种感觉吗？",
    "如果{假设}，你会{选择}？",
    "你觉得{观点}对吗？",
    "这说的是不是你？",
    "留言区说说你的想法",
]


# ========== 加缪语感适配器类 ==========
class CamusStyleAdapter:
    """加缪荒诞哲学语感适配器"""

    @staticmethod
    def detect_ai_flavor(text: str) -> dict:
        """
        检测文案中的AI味浓度

        Returns:
            {
                "has_ai_flavor": bool,
                "ai_words": list[str],
                "score": float  # 0-1，越高越像AI
            }
        """
        ai_words_found = []
        for word in AI_FLAVOR_WORDS:
            if word in text:
                ai_words_found.append(word)

        # 计算AI味分数
        score = min(len(ai_words_found) * 0.2, 1.0)

        # 检测长句比例（加缪风格允许较长句子）
        sentences = re.split(r'[。！？]', text)
        long_sentences = [s for s in sentences if len(s.strip()) > 40]
        if len(sentences) > 0:
            long_ratio = len(long_sentences) / len(sentences)
            score += long_ratio * 0.2  # 降低长句权重

        return {
            "has_ai_flavor": len(ai_words_found) > 0 or score > 0.4,
            "ai_words": ai_words_found,
            "score": min(score, 1.0)
        }

    @staticmethod
    def check_poetic_level(text: str) -> dict:
        """
        检查诗意化程度（替代口语化检测）

        Returns:
            {
                "is_poetic": bool,
                "overly_emotional": bool,
                "sentiment_score": float
            }
        """
        # 检测过度煽情
        overly_emotional = False
        for pattern in OVERLY_EMOTIONAL_PATTERNS:
            if re.search(pattern, text):
                overly_emotional = True
                break

        # 检测感叹号密度
        exclamation_count = text.count('！')
        text_length = len(text)
        exclamation_density = exclamation_count / text_length if text_length > 0 else 0

        # 诗意判断：不过度煽情，有一定节奏
        is_poetic = not overly_emotional and exclamation_density < 0.05

        return {
            "is_poetic": is_poetic,
            "overly_emotional": overly_emotional,
            "exclamation_density": exclamation_density
        }

    @staticmethod
    def check_emoji_density(text: str) -> dict:
        """
        检查Emoji密度（加缪风格要求较低）

        Returns:
            {
                "emoji_count": int,
                "density": float,
                "is_appropriate": bool
            }
        """
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"
            "\U0001F300-\U0001F5FF"
            "\U0001F680-\U0001F6FF"
            "\U0001F1E0-\U0001F1FF"
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+",
            flags=re.UNICODE
        )

        emojis = emoji_pattern.findall(text)
        emoji_count = len(emojis)

        text_only = emoji_pattern.sub('', text)
        text_length = len(text_only)

        # 加缪风格：每150字1个emoji（较低密度）
        density = (emoji_count / text_length * 150) if text_length > 0 else 0

        return {
            "emoji_count": emoji_count,
            "density": density,
            "is_appropriate": density <= 2  # 允许较低密度
        }

    @staticmethod
    def add_emoji_by_emotion(text: str, emotion: str) -> str:
        """
        根据情绪添加合适的emoji（存在主义风格）
        """
        emojis = CAMUS_EMOJI.get(emotion, CAMUS_EMOJI["共鸣"])
        emoji = random.choice(emojis)

        # 在文本末尾添加emoji
        return f"{text} {emoji}"

    @staticmethod
    def add_existential_hook(text: str, **kwargs) -> str:
        """
        添加存在主义互动钩子
        """
        hook = random.choice(EXISTENTIAL_HOOKS)
        try:
            formatted_hook = hook.format(**kwargs)
        except KeyError:
            formatted_hook = hook

        return f"{text}\n{formatted_hook}"

    @staticmethod
    def enhance_poeitic_punctuation(text: str) -> str:
        """
        增强标点符号，添加诗意感（克制版）
        """
        result = text
        sentences = re.split(r'([。！？])', text)

        for i in range(len(sentences)):
            if sentences[i] in '。！？':
                # 将部分感叹号改为句号（克制表达）
                if random.random() < 0.4 and sentences[i] == '！':
                    sentences[i] = '。'
                # 偶尔使用省略号
                elif random.random() < 0.15:
                    sentences[i] = '...'

        return ''.join(sentences)

    @staticmethod
    def adapt_text(
        text: str,
        emotion: str = "共鸣",
        add_hook: bool = False,
        enhance_punc: bool = True
    ) -> str:
        """
        综合适配文案为加缪荒诞哲学风格

        Args:
            text: 原始文案
            emotion: 情绪类型
            add_hook: 是否添加互动钩子
            enhance_punc: 是否增强标点

        Returns:
            适配后的文案
        """
        result = text

        # 添加emoji（较低密度）
        result = CamusStyleAdapter.add_emoji_by_emotion(result, emotion)

        # 增强标点（诗意克制）
        if enhance_punc:
            result = CamusStyleAdapter.enhance_poeitic_punctuation(result)

        # 添加互动钩子（存在主义风格）
        if add_hook:
            result = CamusStyleAdapter.add_existential_hook(result)

        return result

    @staticmethod
    def build_camus_system_prompt(base_system: str) -> str:
        """
        构建加缪风格的系统提示词

        Args:
            base_system: 基础系统提示词

        Returns:
            增强后的系统提示词
        """
        return f"""{base_system}

{CAMUS_STYLE_MODIFIER}

【文案风格要求】
1. 诗意而克制，保持荒诞的清醒
2. 金句密度高，适合截图传播
3. 情感深沉而不煽情
4. 多用"我"的第一人称视角
5. 避免说教感，用提问引发思考

【禁止词汇】
{chr(10).join(f'- {w}' for w in AI_FLAVOR_WORDS[:10])}

【禁止表达】
- 过度乐观的"鸡汤式"总结
- "姐妹们""宝子们"等轻浮称呼
- 连续感叹号和波浪号
"""


# ========== 导出便捷函数 ==========
def detect_and_adapt_camus(text: str, emotion: str = "共鸣") -> dict:
    """
    检测并适配文案为加缪风格

    Returns:
        {
            "original": str,
            "adapted": str,
            "ai_flavor": dict,
            "poetic": dict,
            "emoji": dict
        }
    """
    ai_flavor = CamusStyleAdapter.detect_ai_flavor(text)
    poetic = CamusStyleAdapter.check_poetic_level(text)
    emoji = CamusStyleAdapter.check_emoji_density(text)

    # 根据检测结果决定是否适配
    adapted = text
    if ai_flavor["has_ai_flavor"] or not poetic["is_poetic"] or not emoji["is_appropriate"]:
        adapted = CamusStyleAdapter.adapt_text(
            text,
            emotion=emotion,
            add_hook=True,
            enhance_punc=True
        )

    return {
        "original": text,
        "adapted": adapted,
        "ai_flavor": ai_flavor,
        "poetic": poetic,
        "emoji": emoji
    }
