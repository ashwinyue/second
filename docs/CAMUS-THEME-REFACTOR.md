# 加缪主题重构文档

> 将项目从通用小红书风格重构为加缪荒诞哲学主题

## 📋 重构概览

**日期**: 2026-02-11
**目标**: 将项目主题改为加缪荒诞哲学，专注于存在主义视频内容生成

---

## 🎨 核心设计理念

### 加缪主题定位
- **核心理念**: 荒诞、反抗、自由、激情
- **视觉风格**: 强烈光影对比、孤独疏离感、沙漠与海洋元素
- **文案风格**: 深度拷问、诗意克制、金句密度高

### 配色方案

| 颜色 | 代码 | 寓意 |
|------|------|------|
| 沙漠黄 | `#D4A574` | 西西弗斯的岩石 |
| 深蓝灰 | `#2C3E50` | 理性的沉默 |
| 血橙红 | `#E74C3C` | 反抗的张力 |
| 米白 | `#F5E6D3` | 阿尔及尔的阳光 |
| 深黑 | `#1A1A1A` | 荒诞的底色 |

---

## 📁 文件变更清单

### 1. `app/style_base.py` - 基础风格模块

**变更类型**: 完全重写

**主要变更**:
```python
# 新增加缪主题配色
CAMUS_COLOR_PALETTE = {
    "primary": "#D4A574",      # 沙漠黄
    "secondary": "#2C3E50",    # 深蓝灰
    "accent": "#E74C3C",       # 血橙红
    "background": "#F5E6D3",   # 米白
    "shadow": "#1A1A1A",       # 深黑
}

# 新增加缪金句库
CAMUS_QUOTES = {
    "荒诞": [...],
    "反抗": [...],
    "自由": [...],
    "当下": [...],
}

# 新增函数
- build_camus_system_prompt()     # 构建加缪主题系统提示词
- get_camus_quote(theme)          # 获取加缪金句
- get_color_palette()             # 获取主题配色
```

**删除内容**:
- `MINIMALIST_SUFFIX` (极简风格后缀)
- 原有 `COLOR_PALETTE` (高饱和度配色)
- 原有 `EMOTION_COMPOSITION` (通用情绪构图)

---

### 2. `app/style/templates.py` - 模板库

**变更类型**: 完全重写

**主要变更**:
```python
# 新增深度拷问开头模板
CAMUS_OPENING_TEMPLATES = {
    "absurd": [...],      # 荒诞拷问
    "existence": [...],   # 存在拷问
    "rebellion": [...],   # 反抗拷问
}

# 新增加缪主题结尾三件套
CAMUS_ENDING_TRIAD = {
    "empathy": [...],     # 共情金句
    "twist": [...],       # 反转结尾
    "interaction": [...], # 互动钩子
}

# 新增类
- CamusTemplateGenerator    # 加缪模板生成器
- CamusEndingGenerator      # 加缪结尾生成器

# 新增函数
- build_camus_opening_prompt()  # 构建加缪风格开头提示
- get_camus_quote()            # 获取加缪金句
- get_camus_emoji()            # 获取加缪主题emoji
```

**删除内容**:
- `GOLDEN_3S_TEMPLATES` (通用黄金三秒模板)
- `ENDING_INTERACTION_TRIAD` (通用结尾三件套)
- `Golden3sTemplateGenerator` 类
- `EndingGenerator` 类
- `build_golden_3s_prompt()` 函数

---

### 3. `app/style/xiaohongshu.py` - 语感适配器

**变更类型**: 完全重写

**主要变更**:
```python
# 新增加缪语感强制规则
CAMUS_STYLE_MODIFIER = """
1. 诗意克制：避免过度修饰
2. 标点符号：克制使用感叹号
3. Emoji密度：每150字1个
4. 称呼体系：避免"姐妹们"等轻浮称呼
5. 互动钩子：哲学式追问
"""

# 新增加缪主题表情库
CAMUS_EMOJI = {
    "荒诞": ["🤔", "🌊", "🏜️", "🖤"],
    "反抗": ["🔥", "⚡", "👊", "🌅"],
    "自由": ["🕊️", "✨", "🌬️", "💫"],
    "共鸣": ["🙌", "❤️", "🤝", "🕯️"],
}

# 新增类
- CamusStyleAdapter    # 加缪语感适配器

# 新增函数
- detect_and_adapt_camus()  # 检测并适配为加缪风格
```

**删除内容**:
- `XHS_STYLE_MODIFIER` (小红书语感规则)
- `XiaohongshuStyleAdapter` 类
- `detect_and_adapt()` 函数
- 原有的口语化检测逻辑

---

### 4. `app/workflow/nodes/writer.py` - 文案生成节点

**变更类型**: 完全重写

**主要变更**:
```python
# 新增配置
theme = config.get('camus_theme', '荒诞')  # 荒诞/反抗/自由/当下

# 新增系统提示词
CAMUS_SYSTEM = build_camus_system_prompt()

# 新增导入
from ...style_base import build_camus_system_prompt, get_camus_quote
from ...style.xiaohongshu import CamusStyleAdapter
from ...style.templates import build_camus_opening_prompt, CamusTemplateGenerator

# 新增逻辑
- 使用深度拷问开头指导
- 获取加缪金句作为参考
- 检测诗意程度（替代口语化检测）
- 加缪风格适配
```

**删除内容**:
- `XHS_SYSTEM_ENHANCED` 系统提示词
- `enable_xhs_style` 配置
- `XiaohongshuStyleAdapter` 使用
- `Golden3sTemplateGenerator` 使用
- `build_golden_3s_prompt()` 调用

---

### 5. `app/style/__init__.py` - 模块导出

**变更类型**: 完全重写

**主要变更**:
```python
# 新增导出
from .xiaohongshu import (
    CamusStyleAdapter,
    CAMUS_STYLE_MODIFIER,
    detect_and_adapt_camus,
)
from .templates import (
    build_camus_opening_prompt,
    CamusEndingGenerator,
    CamusTemplateGenerator,
    get_camus_emoji,
    get_all_opening_types,
    CAMUS_OPENING_TEMPLATES,
    CAMUS_ENDING_TRIAD,
)
```

**删除导出**:
- `XiaohongshuStyleAdapter`
- `XHS_STYLE_MODIFIER`
- `detect_and_adapt`
- `build_golden_3s_prompt`
- `EndingGenerator`
- `Golden3sTemplateGenerator`

---

## 🔌 API 变更

### 配置参数变更

| 原参数 | 新参数 | 说明 |
|--------|--------|------|
| `enable_xhs_style` | `camus_theme` | 启用小红书风格 → 加缪主题类型 |
| `philosopher` | `camus_theme` | 哲学家名称 → 加缪主题 |
| N/A | `theme` | 新增：荒诞/反抗/自由/当下 |

### 函数签名变更

```python
# 旧版
detect_and_adapt(text: str, emotion: str = "共鸣") -> dict

# 新版
detect_and_adapt_camus(text: str, emotion: str = "共鸣") -> dict
```

```python
# 旧版
build_golden_3s_prompt(topic: str, philosopher: str = "", template_type: str = "auto") -> str

# 新版
build_camus_opening_prompt(topic: str, theme: str = "荒诞") -> str
```

---

## 📊 加缪金句库

### 荒诞主题
- 荒诞源于人类渴望与世界理智沉默之间的对立
- 世界只是一片陌生的景物，我的精神在此无依无靠
- 我不是这里的人，也不是别处的
- 人对生存状况的尴尬与无奈有清醒的意识

### 反抗主题
- 没有什么命运是无法被蔑视的
- 反抗使生命拥有价值
- 我们必须想象西西弗斯是幸福的
- 攀登顶峰的奋斗本身，便充实了人的心灵

### 自由主题
- 识别荒诞，即承认局限与世界的无理
- 对未来的真实慷慨，是将一切献给现在
- 真正的自由，是与荒诞共处

### 当下主题
- 没有生存的痛苦，就不会热爱生命
- 活得好不如活得丰富
- 在清醒的冷漠中生活，既是荒诞者的美德

---

## 🎯 使用示例

### 生成加缪主题文案

```python
from app.style import CamusTemplateGenerator, get_camus_quote
from app.style.xiaohongshu import detect_and_adapt_camus

# 获取加缪金句
quote = get_camus_quote("荒诞")
print(quote)  # 荒诞源于人类渴望与世界理智沉默之间的对立

# 生成开头
opening = CamusTemplateGenerator.get_example_opening("荒诞")
print(opening)  # 你有没有过一种感觉，明明活着，却找不到意义？

# 适配文案风格
result = detect_and_adapt_camus("你的文案内容", emotion="共鸣")
print(result["adapted"])
```

### 配置工作流

```python
config = {
    "topic": "人生的意义",
    "camus_theme": "荒诞",  # 荒诞/反抗/自由/当下
}
```

---

## 🔄 迁移指南

### 对于现有代码

1. **替换导入**:
```python
# 旧版
from app.style import XiaohongshuStyleAdapter, build_golden_3s_prompt

# 新版
from app.style import CamusStyleAdapter, build_camus_opening_prompt
```

2. **更新配置**:
```python
# 旧版
config = {"enable_xhs_style": True, "philosopher": "加缪"}

# 新版
config = {"camus_theme": "荒诞"}
```

3. **更新函数调用**:
```python
# 旧版
result = detect_and_adapt(text, emotion="共鸣")

# 新版
result = detect_and_adapt_camus(text, emotion="共鸣")
```

---

## 📝 待完成事项

- [ ] 更新 `app/api/main.py` 中的配置参数
- [ ] 更新测试文件以匹配新的主题
- [ ] 更新文档中的示例代码
- [ ] 验证 TTS 服务与加缪主题的兼容性
- [ ] 更新前端界面以支持主题选择

---

## 📚 参考资源

- **加缪作品**: 《局外人》《西西弗神话》《鼠疫》
- **哲学概念**: 荒诞主义、存在主义、反抗哲学
- **视觉风格**: 阿尔及尔阳光、沙漠意象、西西弗斯神话
