"""
通用文案框架 - 基于"黄金3秒"理论和爆款文案研究
实现灵活的文案生成框架，支持多种钩子类型和结构模式
"""
import re
import random
from typing import Literal


# ============================================================================
# 黄金3秒钩子类型（基于爆款文案研究）
# ============================================================================
GOLDEN_3S_HOOKS = {
    "curiosity": {
        "name": "好奇心钩子",
        "description": "用悬念引发好奇，提高完播率",
        "templates": [
            "你绝对想不到{现象}",
            "{主体}竟然{意外结果}？",
            "为什么{现象}会{结果}？",
            "90%的人都不知道的{真相}",
            "揭秘{现象}的真相",
        ],
    },
    "contrast": {
        "name": "反差钩子",
        "description": "制造强烈反差冲击，引发认知冲突",
        "templates": [
            "明明{正常状态}，却{异常结果}",
            "同样的{条件}，为什么{反差结果}？",
            "{表面现象}背后，竟是{真相}",
            "你以为{认知}，其实{反转}",
            "{预期}？事实却是{现实}",
        ],
    },
    "question": {
        "name": "疑问钩子",
        "description": "用提问引发思考和代入感",
        "templates": [
            "你有没有{经历}？",
            "如果{假设}，你会{选择}吗？",
            "为什么{现象}，我们却{反应}？",
            "{终极问题}，你思考过吗？",
            "真的是{现象}吗？",
        ],
    },
    "data": {
        "name": "数据钩子",
        "description": "用数据/事实建立权威感",
        "templates": [
            "{数字}%的人都在{现象}",
            "研究发现{事实}",
            "{时间}后，{结果}",
            "据说{事实}",
            "数据告诉你{真相}",
        ],
    },
    "emotional": {
        "name": "情绪钩子",
        "description": "直接触发情绪共鸣",
        "templates": [
            "每次{现象}，都{感受}",
            "最让人{情绪}的，是{现象}",
            "不敢相信，竟然{现象}",
            "{感受}！{现象}太真实了",
            "谁懂{现象}的心情",
        ],
    },
}


# ============================================================================
# 情绪钩子类型
# ============================================================================
EMOTIONAL_HOOKS = {
    "empathy": {
        "name": "共鸣钩子",
        "description": "让观众觉得'这说的就是我'",
        "triggers": ["你有没有", "谁懂", "是不是", "这说的是不是你"],
    },
    "anxiety": {
        "name": "焦虑钩子",
        "description": "触发担忧和紧迫感",
        "triggers": ["再不...就", "警惕", "小心", "千万别"],
    },
    "hope": {
        "name": "希望钩子",
        "description": "提供解决方案和正向预期",
        "triggers": ["终于", "原来", "竟然可以", "破解"],
    },
    "surprise": {
        "name": "惊喜钩子",
        "description": "意外发现和新认知",
        "triggers": ["竟然", "居然", "想不到", "没想到"],
    },
    "regret": {
        "name": "后悔钩子",
        "description": "引发'早知道就好了'的感受",
        "triggers": ["早知道", "后悔", "可惜", "要是"],
    },
}


# ============================================================================
# 文案结构框架（基于爆款文案研究）
# ============================================================================
COPY_FRAMEWORKS = {
    "hook_value": {
        "name": "钩子-价值型",
        "structure": ["hook", "pain", "solution", "value", "cta"],
        "description": "痛点-解决方案-价值-行动，适合干货科普",
    },
    "story_twist": {
        "name": "故事-反转型",
        "structure": ["hook", "story", "twist", "insight", "cta"],
        "description": "故事铺垫-意外反转-深度洞察，适合情感内容",
    },
    "question_answer": {
        "name": "问答-科普型",
        "structure": ["hook", "question", "explain", "example", "summary"],
        "description": "提问-解释-举例-总结，适合知识输出",
    },
    "emotion_resonance": {
        "name": "情感-共鸣型",
        "structure": ["hook", "emotion", "story", "empathy", "healing"],
        "description": "情感铺垫-故事-共情-治愈，适合情感疗愈",
    },
    "minimal_punchy": {
        "name": "极简-金句型",
        "structure": ["hook", "insight", "golden_line", "cta"],
        "description": "钩子-洞察-金句-互动，适合快节奏内容",
    },
    "contrast_insight": {
        "name": "反差-洞察型",
        "structure": ["hook", "contrast", "deep_dive", "paradigm_shift", "cta"],
        "description": "反差制造-深度分析-认知升级，适合深度思考",
    },
}


# ============================================================================
# 互动钩子（结尾CTA）
# ============================================================================
CTA_HOOKS = {
    "question": [
        "这说的是不是你？留言区说说👇",
        "你也有过这样的感受吗？来聊聊～",
        "认同的点个赞，不认同的来辩～",
        "谁懂这种感觉？评论区见👇",
        "你觉得呢？说说你的看法",
    ],
    "share": [
        "收藏起来，难过的时候看看",
        "转发给需要的人",
        "点赞收藏，下次想看不迷路",
        "让更多人看到",
        "分享给你在乎的人",
    ],
    "follow": [
        "点赞关注，不迷路✨",
        "关注我，下次分享更多好内容",
        "下期更精彩，关注不迷路",
        "点个关注，一起变好",
    ],
}


# ============================================================================
# 节奏控制（文案节奏模式）
# ============================================================================
RHYTHM_PATTERNS = {
    "fast": {
        "name": "快节奏",
        "description": "短句为主，信息密度高",
        "sentence_length": "8-15字",
        "punctuation": "多用感叹号和问号",
    },
    "medium": {
        "name": "中等节奏",
        "description": "长短句结合，张弛有度",
        "sentence_length": "15-25字",
        "punctuation": "句号和逗号为主",
    },
    "slow": {
        "name": "慢节奏",
        "description": "长句为主，娓娓道来",
        "sentence_length": "25-40字",
        "punctuation": "句号和省略号为主",
    },
}


# ============================================================================
# 文案检测和优化工具
# ============================================================================

class CopyAnalyzer:
    """文案分析器"""

    @staticmethod
    def check_golden_3s(text: str) -> dict:
        """检测开头是否符合黄金3秒原则"""
        # 使用正则表达式分割句子
        sentences = re.split(r'[。！？]', text)
        first_sentence = sentences[0] if sentences else ""

        # 检测钩子类型
        hook_found = None
        for hook_type, config in GOLDEN_3S_HOOKS.items():
            for trigger in config["templates"]:
                # 简化匹配逻辑
                if any(word in first_sentence for word in ["你", "为什么", "竟然", "竟然", "据说"]):
                    hook_found = hook_type
                    break

        return {
            "has_hook": hook_found is not None,
            "hook_type": hook_found,
            "first_sentence_length": len(first_sentence),
            "is_golden_3s": len(first_sentence) <= 50,  # 黄金3秒约50字
        }

    @staticmethod
    def check_emotional_resonance(text: str) -> dict:
        """检测情绪共鸣点"""
        emotions_found = []
        for emotion_name, config in EMOTIONAL_HOOKS.items():
            for trigger in config["triggers"]:
                if trigger in text:
                    emotions_found.append(emotion_name)

        return {
            "emotions": emotions_found,
            "has_emotional_hook": len(emotions_found) > 0,
        }

    @staticmethod
    def suggest_improvements(analysis: dict) -> list[str]:
        """根据分析结果提供改进建议"""
        suggestions = []

        golden_3s = analysis.get("golden_3s", {})
        if not golden_3s.get("has_hook", False):
            suggestions.append("建议在开头添加钩子（疑问/反差/好奇心）")

        if golden_3s.get("first_sentence_length", 0) > 50:
            suggestions.append("开头过长，建议控制在50字以内（黄金3秒）")

        emotional = analysis.get("emotional", {})
        if not emotional.get("has_emotional_hook", False):
            suggestions.append("建议添加情绪钩子增强共鸣")

        return suggestions


# ============================================================================
# 框架构建器
# ============================================================================

class FrameworkBuilder:
    """文案框架构建器"""

    @staticmethod
    def get_hook_template(hook_type: str = "curiosity") -> str:
        """获取钩子模板"""
        if hook_type not in GOLDEN_3S_HOOKS:
            hook_type = "curiosity"
        return random.choice(GOLDEN_3S_HOOKS[hook_type]["templates"])

    @staticmethod
    def get_framework_structure(framework_name: str = "minimal_punchy") -> list[str]:
        """获取文案框架结构"""
        if framework_name not in COPY_FRAMEWORKS:
            framework_name = "minimal_punchy"
        framework = COPY_FRAMEWORKS[framework_name]
        return framework["structure"]

    @staticmethod
    def get_cta_hook(cta_type: str = "question") -> str:
        """获取互动钩子"""
        if cta_type not in CTA_HOOKS:
            cta_type = "question"
        return random.choice(CTA_HOOKS[cta_type])

    @staticmethod
    def build_framework_prompt(
        topic: str,
        framework: str = "minimal_punchy",
        hook_type: str = "curiosity",
        **kwargs
    ) -> str:
        """构建框架化提示词"""
        structure = FrameworkBuilder.get_framework_structure(framework)
        hook_template = FrameworkBuilder.get_hook_template(hook_type)

        framework_info = COPY_FRAMEWORKS[framework]

        return f"""【文案框架：{framework_info['name']}】
框架结构：{' → '.join(structure)}
描述：{framework_info['description']}

主题：{topic}

开头钩子参考：{hook_template}

要求：
1. 严格按照框架结构推进
2. 开头3秒必须用钩子抓住注意力
3. 每个环节自然衔接，不生硬
4. 根据框架类型调整语气和节奏
"""


# ============================================================================
# 导出便捷函数
# ============================================================================

def get_available_hooks() -> dict:
    """获取所有可用的钩子类型"""
    return {
        k: v["description"]
        for k, v in GOLDEN_3S_HOOKS.items()
    }


def get_available_frameworks() -> dict:
    """获取所有可用的文案框架"""
    return {
        k: v["description"]
        for k, v in COPY_FRAMEWORKS.items()
    }


def get_available_emotions() -> dict:
    """获取所有可用的情绪钩子"""
    return {
        k: v["description"]
        for k, v in EMOTIONAL_HOOKS.items()
    }
