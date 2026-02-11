# 多风格系统文档

## 概述

项目从单一的加缪荒诞哲学风格重构为支持多种风格的可插拔系统。该系统基于"黄金3秒"钩子理论和爆款文案框架研究，支持哲学类、情感类、知识类、娱乐类、成长类等多种风格。

## 设计理念

### 解决的问题

1. **固化问题**：原有系统所有视频使用相同的模板，导致内容千篇一律
2. **风格单一**：只有加缪一种风格选项，无法满足不同内容需求
3. **质量不足**：原有小红书风格文案质量有待提升

### 解决方案

1. **可插拔风格系统**：通过 `StyleConfig` 数据类定义风格，支持动态注册
2. **黄金3秒框架**：基于爆款文案研究的开头钩子理论
3. **多样化预设**：提供6种预设风格，涵盖主流内容类型

## 架构设计

### 文件结构

```
app/style/
├── __init__.py         # 导出所有风格相关功能
├── frameworks.py       # 通用文案框架（黄金3秒、情绪钩子）
├── presets.py         # 风格预设配置
├── xiaohongshu.py     # 加缪风格语感适配器
└── templates.py       # 加缪风格模板库

app/style_base.py       # 风格管理模块（多风格支持）
app/workflow/nodes/writer.py  # 文案生成节点（多风格支持）
```

### 核心模块

#### 1. frameworks.py - 文案框架

**黄金3秒钩子类型**：
- `curiosity`: 好奇心钩子 - "你绝对想不到..."
- `contrast`: 反差钩子 - "明明...却..."
- `question`: 疑问钩子 - "你有没有...？"
- `data`: 数据钩子 - "90%的人都..."
- `emotional`: 情绪钩子 - "每次...都..."

**文案框架类型**：
- `hook_value`: 钩子-价值型
- `story_twist`: 故事-反转型
- `question_answer`: 问答-科普型
- `emotion_resonance`: 情感-共鸣型
- `minimal_punchy`: 极简-金句型
- `contrast_insight`: 反差-洞察型

#### 2. presets.py - 风格预设

**支持的风格**：

| 风格 | 类别 | 描述 | 适用场景 |
|------|------|------|----------|
| `camus` | philosophy | 加缪荒诞哲学 - 深度拷问、诗意克制 | 哲学思考、存在主义 |
| `healing` | emotion | 温暖治愈 - 亲切陪伴、温柔鼓励 | 情感抚慰、治愈系 |
| `knowledge` | knowledge | 硬核科普 - 权威数据、逻辑清晰 | 知识输出、干货科普 |
| `humor` | entertainment | 幽默搞笑 - 反转套路、轻松调侃 | 搞笑内容、娱乐互动 |
| `growth` | growth | 成长觉醒 - 认知升级、行动导向 | 励志成长、自我突破 |
| `minimal` | philosophy | 极简金句 - 短小精悍、直击人心 | 金句输出、极简风格 |

**StyleConfig 配置项**：

```python
@dataclass
class StyleConfig:
    # 基本信息
    name: str                      # 风格名称
    category: Literal              # 风格类别
    description: str               # 描述

    # 视觉风格
    visual_suffix: str             # 视觉后缀（动漫、写实等）
    color_palette: dict            # 配色方案
    emotion_composition: dict      # 情绪构图映射

    # 文案风格
    tone: str                      # 语调
    emoji_density: float           # emoji密度
    use_emoji: bool                # 是否使用emoji
    punctuation_style: Literal     # 标点风格

    # 开头/结尾配置
    hook_types: list[str]          # 钩子类型列表
    ending_types: list[str]        # 结尾类型列表
    framework: str                 # 文案框架

    # 系统提示词
    system_prompt: str             # LLM系统提示词

    # 金句库和表情库
    quotes: dict[str, list[str]]   # 金句库
    emojis: dict[str, list[str]]   # 表情库
```

## 使用方法

### 基础用法

```python
from app.style import (
    get_style_config,
    build_stylized_prompt,
    build_system_prompt,
)

# 获取风格配置
config = get_style_config("healing")

# 构建系统提示词
system_prompt = build_system_prompt("healing")

# 构建风格化图像提示词
image_prompt = build_stylized_prompt(
    base_prompt="一个人坐在窗边思考",
    emotion="温暖",
    style="healing"
)
```

### API 调用

```python
# 在 config 中指定风格
config = {
    "topic": "如何应对焦虑",
    "style": "healing",  # 使用温暖治愈风格
    "theme": "治愈",     # 可选：子主题
}

# 文案生成节点会自动使用对应风格的系统提示词和金句
```

### 添加新风格

```python
from app.style.presets import StyleConfig, STYLE_PRESETS

# 定义新风格配置
NEW_STYLE_CONFIG = StyleConfig(
    name="new_style",
    category="emotion",
    description="新风格描述",
    visual_suffix="...",
    color_palette={...},
    emotion_composition={...},
    tone="...",
    hook_types=["curiosity", "question"],
    ending_types=["empathy", "cta"],
    framework="minimal_punchy",
    system_prompt="""系统提示词...""",
    quotes={...},
    emojis={...},
)

# 注册新风格
STYLE_PRESETS["new_style"] = NEW_STYLE_CONFIG
```

## 迁移指南

### 从旧系统迁移

**旧代码**（仅支持加缪风格）：
```python
config = {
    "topic": "生命的意义",
    "camus_theme": "荒诞",
}
```

**新代码**（支持多种风格）：
```python
config = {
    "topic": "生命的意义",
    "style": "camus",      # 风格名称
    "theme": "荒诞",       # 可选：子主题
}
```

### 风格名称映射

| 旧配置 | 新风格名称 |
|--------|-----------|
| `camus_theme: "荒诞"` | `style: "camus", theme: "荒诞"` |
| 无对应 | `style: "healing"` |
| 无对应 | `style: "knowledge"` |
| 无对应 | `style: "humor"` |
| 无对应 | `style: "growth"` |
| 无对应 | `style: "minimal"` |

## 研究基础

### 黄金3秒理论

短视频前3秒决定了用户是否继续观看。开头必须：
- 用钩子抓住注意力
- 引发好奇心或情绪共鸣
- 避免冗长铺垫

### 情绪钩子类型

- **共鸣钩子**："这说的就是我"
- **焦虑钩子**："再不...就..."
- **希望钩子**："原来可以..."
- **惊喜钩子**："竟然..."
- **后悔钩子**："早知道..."

### 爆款文案结构

1. **钩子-价值型**：痛点-解决方案-价值-行动
2. **故事-反转型**：故事-意外反转-深度洞察
3. **问答-科普型**：提问-解释-举例-总结
4. **情感-共鸣型**：情感-故事-共情-治愈
5. **极简-金句型**：钩子-洞察-金句-互动

## 扩展性

系统设计支持无限扩展：

1. **添加新风格**：在 `presets.py` 中定义新的 `StyleConfig`
2. **添加新钩子**：在 `frameworks.py` 的 `GOLDEN_3S_HOOKS` 中添加
3. **添加新框架**：在 `frameworks.py` 的 `COPY_FRAMEWORKS` 中添加

## 向后兼容

系统保持与旧代码的向后兼容：

- `camus_theme` 参数仍可使用
- 原有加缪风格函数保持不变
- 默认行为保持一致

## 示例输出

### 加缪风格 (camus)

```
你有没有过一种感觉，明明活着，却找不到意义？

荒诞源于人类渴望与世界沉默之间的对立。我们必须想象西西弗斯是幸福的。🏜️
```

### 温暖治愈风格 (healing)

```
每次觉得累的时候，都想躲起来...

但你已经做得很好了。慢慢来，比较快。🌸
```

### 硬核科普风格 (knowledge)

```
研究发现，90%的人都在无效学习。

什么是有效学习？数据告诉你真相。📊
```

### 幽默搞笑风格 (humor)

```
心态崩了，但还要保持微笑...

这不就是生活吗？笑一笑就过去了。😂
```

### 成长觉醒风格 (growth)

```
明明同样努力，为什么结果不同？

认知升级，才能突破舒适区。🚀
```

### 极简金句风格 (minimal)

``少即是多。

复杂是简单不够的结果。💡
```
