# 小红书语感适配器 & 黄金三秒模板库

## 文档概述

本文档记录哲学科普视频生成 Agent 的小红书风格优化模块，包括**语感适配器**和**黄金三秒模板库**的设计与实现。

**版本**: v1.0
**更新日期**: 2025-02-11

---

## 一、背景与目标

### 1.1 问题分析

通过分析小红书平台爆款内容，发现以下关键特征：

| 维度 | 爆款特征 | 原有工作流差距 |
|-----|---------|--------------|
| **开头** | 黄金三秒（反常识/数字结果/情绪引爆/深度拷问） | ❌ 缺乏结构化开头模板 |
| **语感** | 口语化、短句为主、闺蜜聊天感 | ❌ AI味浓、长句多 |
| **标点** | 每2-3句一个!或～ | ❌ 标点平淡 |
| **Emoji** | 每100字1-3个 | ❌ 缺乏情绪化符号 |
| **互动** | 结尾强制互动钩子 | ❌ 缺乏用户引导 |

### 1.2 优化目标

- ✅ 降低 AI 味浓度 50%+
- ✅ 完播率提升至 60%+
- ✅ 支持一键切换平台风格（小红书/通用）

---

## 二、模块架构

### 2.1 文件结构

```
app/style/
├── __init__.py              # 模块导出（整合 base.py 和新模块）
├── base.py                  # 原有风格模块（从 style.py 迁移）
├── xiaohongshu.py           # 🆕 小红书语感适配器
└── templates.py             # 🆕 黄金三秒模板库
```

### 2.2 模块依赖关系

```
┌─────────────────────────────────────────────────────────┐
│                   app/workflow/nodes                    │
│                                                         │
│  writer.py                                              │
│    ├── imports: build_stylized_prompt                  │
│    ├── imports: XiaohongshuStyleAdapter                │
│    └── imports: Golden3sTemplateGenerator               │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                      app/style                          │
│                                                         │
│  __init__.py ─────────────────────────────────────────┐  │
│    ├── exports: build_stylized_prompt (base.py)      │  │
│    ├── exports: XiaohongshuStyleAdapter              │  │
│    └── exports: Golden3sTemplateGenerator             │  │
│                                                         │
│  xiaohongshu.py ─────────────────────────────────────┐  │
│    ├── detect_ai_flavor()                            │  │
│    ├── check_colloquial_level()                      │  │
│    ├── check_emoji_density()                         │  │
│    └── adapt_text()                                  │  │
│                                                         │
│  templates.py ──────────────────────────────────────┐  │
│    ├── GOLDEN_3S_TEMPLATES                          │  │
│    ├── build_golden_3s_prompt()                     │  │
│    └── EndingGenerator                              │  │
└─────────────────────────────────────────────────────────┘
```

---

## 三、小红书语感适配器

### 3.1 核心功能

#### 3.1.1 AI 味检测

```python
from app.style.xiaohongshu import XiaohongshuStyleAdapter

# 检测文案中的AI味
result = XiaohongshuStyleAdapter.detect_ai_flavor(
    "综上所述，我们需要努力工作才能成功"
)
# 返回: {
#     "has_ai_flavor": True,
#     "ai_words": ["综上所述"],
#     "score": 0.15
# }
```

**AI 味检测词库**：
- 综上所述、由此可见、值得注意的是
- 首先...其次...最后、一方面...另一方面
- 让我们、总而言之

#### 3.1.2 口语化检测

```python
result = XiaohongshuStyleAdapter.check_colloquial_level(
    "这是一个非常长的句子，包含了很多复杂的词汇和结构"
)
# 返回: {
#     "colloquial_ratio": 0.0,
#     "is_colloquial": False,
#     "long_sentences": ["这是一个非常长的句子..."]
# }
```

**口语化标准**：
- 短句占比 ≥ 70%
- 单句长度 ≤ 20 字为短句
- 单句长度 > 30 字为长句

#### 3.1.3 Emoji 密度检测

```python
result = XiaohongshuStyleAdapter.check_emoji_density("你好世界")
# 返回: {
#     "emoji_count": 0,
#     "density": 0.0,
#     "is_appropriate": False
# }
```

**Emoji 标准**：
- 每 100 字 1-3 个 emoji
- 过少缺乏情绪，过多像刷屏

#### 3.1.4 文案适配

```python
# 综合适配文案
adapted = XiaohongshuStyleAdapter.adapt_text(
    text="痛苦是成长的必经之路",
    emotion="共鸣",
    add_address=True,    # 添加称呼语
    add_hook=True,       # 添加互动钩子
    enhance_punc=True    # 增强标点
)
# 返回: "宝子们，痛苦是成长的必经之路💕\n你有过这种感觉吗？"
```

**适配策略**：
| 策略 | 说明 | 示例 |
|-----|------|------|
| 称呼语 | 随机选择"宝子们/姐妹们/家人们" | "宝子们，" |
| Emoji | 根据情绪添加对应emoji | "💕" (共鸣) |
| 标点增强 | 句号→感叹号，添加波浪号 | "！～" |
| 互动钩子 | 结尾添加问句或指令 | "你认同吗？" |

### 3.2 情绪-Emoji 映射

```python
EMOJI_BY_EMOTION = {
    "困惑": ["🤔", "❓", "🙀", "😖"],
    "顿悟": ["💡", "✨", "🎯", "🔥"],
    "震撼": ["🤯", "😱", "💥", "🌟"],
    "温柔": ["💕", "🌸", "🍃", "☁️"],
    "沉重": ["😔", "🌧️", "🎭", "🖤"],
    "共鸣": ["🙌", "💪", "❤️", "👏"],
}
```

---

## 四、黄金三秒模板库

### 4.1 四类开头模板

#### 4.1.1 反常识类

```python
from app.style.templates import Golden3sTemplateGenerator

opening = Golden3sTemplateGenerator.generate_opening(
    template_type="anti_common_sense",
    topic="自由",
    反常识事实="你以为自由是想干嘛就干嘛？",
    颠覆性真相="真正的自由是自律",
    错误认知="自由就是无拘无束"
)
# 示例输出:
# "你敢信吗？你以为自由是想干嘛就干嘛？其实真正的自由是自律！"
```

**模板结构**：
- "你敢信吗？{反常识事实}"
- "{普世观点}？其实{颠覆性真相}！"
- "我以前也觉得{错误认知}，直到{转折事件}"

**哲学领域示例**：
- 你敢信吗？痛苦其实是你最忠实的朋友！
- 努力就能成功？其实这是个最大的谎言！
- 我以前也觉得自由就是想干嘛就干嘛，直到我读了叔本华

#### 4.1.2 数字+结果类

```python
opening = Golden3sTemplateGenerator.generate_opening(
    template_type="number_result",
    数字="3",
    误区="思维误区",
    痛苦结果="焦虑"
)
# 示例输出:
# "这3个思维误区，是你一直焦虑的原因！"
```

**模板结构**：
- "这{N}个{误区/坑/错误}，是你一直{痛苦结果}的原因！"
- "{时间/天/步}做到{结果}，这{N}点绝了"

**哲学领域示例**：
- 这3个思维误区，是你一直焦虑的原因！
- 30秒读懂存在主义，这1点绝了
- 2个动作，让你的虚无感消失

#### 4.1.3 情绪引爆类

```python
opening = Golden3sTemplateGenerator.generate_opening(
    template_type="emotion_trigger",
    反常规行动="我放弃了世俗成功",
    意外理由="只为寻找人生的意义"
)
# 示例输出:
# "我放弃了世俗成功，只为寻找人生的意义"
```

**子类型**：
| 子类型 | 模板 | 示例 |
|-------|------|------|
| 傲慢 | 我{反常规行动}，只为{意外理由} | 我辞掉国企工作，只为寻找理想 |
| 愤怒 | 受够{现象}了 | 受够内卷了 |
| 懒惰 | 这{N}个懒人{方法} | 这1个懒人早餐法 |
| 嫉妒 | TA{条件}不如我 | TA学历不如我，却月入过万 |

#### 4.1.4 深度拷问类

```python
opening = Golden3sTemplateGenerator.generate_opening(
    template_type="deep_question",
    共鸣场景="明明很努力，却越来越累"
)
# 示例输出:
# "你有没有过一种感觉，明明很努力，却越来越累？"
```

**模板结构**：
- "你有没有{共鸣场景}？"
- "为什么{反常现象}？真相扎心了"
- "如果{假设场景}，你会{选择}？"

**哲学领域示例**：
- 你有没有过一种感觉，明明很努力，却越来越累？
- 为什么自由越多，我们越不快乐？真相扎心了
- 如果生命没有意义，你还会努力活着吗？

### 4.2 哲学家-模板映射

```python
# 根据哲学家自动推荐模板类型
 PHILOSOPHER_MAPPING = {
    "叔本华": "anti_common_sense",  # 反常识（否定意志）
    "尼采": "emotion_trigger",      # 情绪引爆（超人意志）
    "加缪": "deep_question",        # 深度拷问（荒诞主义）
    "萨特": "deep_question",        # 深度拷问（存在主义）
    "康德": "number_result",        # 数字结果（理性分析）
}
```

### 4.3 互动结尾三件套

```python
from app.style.templates import EndingGenerator

# 生成完整结尾（共情+反转+互动）
ending = EndingGenerator.generate_full_ending(
    价值词="爱",
    金句定义="不是占有，而是成全",
    表面现象="他的离开",
    真相="让我学会了独立",
    场景="这种失去"
)
# 示例输出:
# 真正的爱，不是占有，而是成全
# 谢谢他的离开，让我学会了独立
# 你有过这种失去吗？留言区说说你的故事👇
```

**三件套结构**：

| 组件 | 作用 | 示例 |
|-----|------|------|
| **共情金句** | 情绪共鸣 | "真正的爱，是成全不是占有" |
| **反转结尾** | 颠期预期 | "谢谢他的离开，让我成长" |
| **互动钩子** | 引导评论 | "你认同吗？来辩～" |

---

## 五、工作流集成

### 5.1 配置参数

在 API 请求中添加配置：

```python
# app/api/models.py

class GenerationRequest(BaseModel):
    topic: str
    philosopher: Optional[str] = None
    science_type: Optional[str] = None
    style_preset: Optional[str] = "暗黑治愈"

    # 🆕 小红书风格配置
    enable_xhs_style: bool = True  # 启用小红书语感适配
```

### 5.2 文案生成流程

```python
# app/workflow/nodes/writer.py

async def writer_node(state: AgentState) -> dict:
    # 1. 构建黄金三秒指导（如果启用小红书风格）
    golden_3s_guidance = ""
    if enable_xhs_style:
        golden_3s_guidance = build_golden_3s_prompt(
            topic=topic,
            philosopher=philosopher,
            template_type=随机选择模板类型
        )

    # 2. LLM 生成原始文案
    result = await llm.generate_json(
        prompt=f"{golden_3s_guidance}\n主题：{topic}",
        system_prompt=XHS_SYSTEM_ENHANCED  # 小红书风格提示词
    )

    # 3. 语感适配每个场景
    for i, scene in enumerate(result["scenes"]):
        adapted_text = XiaohongshuStyleAdapter.adapt_text(
            text=scene["text"],
            emotion=scene["emotion"],
            add_address=(i == 0),      # 第一句添加称呼
            add_hook=(i == len(scenes)-1)  # 最后句添加互动
        )
        scene["text"] = adapted_text
```

### 5.3 系统提示词

```python
XHS_SYSTEM_ENHANCED = """你是哲学科普视频文案创作者，专攻小红书平台。

【小红书语感强制规则】
1. 口语化程度：短句占比>70%，避免"综上所述""让我们"等AI词
2. 标点符号：每2-3句必须一个!或～，增强情绪感
3. Emoji密度：每100字至少1个，但不超过3个
4. 称呼体系：使用"姐妹们""宝子们"，营造闺蜜感
5. 互动钩子：在结尾处嵌入问句或"打在评论区"
6. 标题结构：痛点场景+解决方案+好奇缺口

【禁止词汇】
- 综上所述
- 由此可见
- 让我们
- 值得注意的是
- 总的来说
"""
```

---

## 六、效果验证

### 6.1 语感适配测试

```
输入: 综上所述，我们需要努力工作才能成功

输出: 宝子们，综上所述，我们需要努力工作才能成功👏
       你有过这种感觉吗？

AI味分数: 0.30 → 适配成功
```

### 6.2 模板生成测试

```
主题: 生命的意义
哲学家: 加缪
模板类型: deep_question

生成: 你有没有过一种感觉，明明活着，却找不到意义？
       真相扎心了，也许意义本身就不存在...
```

---

## 七、API 参考

### 7.1 XiaohongshuStyleAdapter

```python
class XiaohongshuStyleAdapter:
    """小红书语感适配器"""

    @staticmethod
    def detect_ai_flavor(text: str) -> dict:
        """检测AI味浓度"""

    @staticmethod
    def check_colloquial_level(text: str) -> dict:
        """检查口语化程度"""

    @staticmethod
    def check_emoji_density(text: str) -> dict:
        """检查Emoji密度"""

    @staticmethod
    def adapt_text(
        text: str,
        emotion: str = "共鸣",
        add_address: bool = False,
        add_hook: bool = False,
        enhance_punc: bool = True
    ) -> str:
        """综合适配文案"""
```

### 7.2 Golden3sTemplateGenerator

```python
class Golden3sTemplateGenerator:
    """黄金三秒模板生成器"""

    @staticmethod
    def get_template_type() -> str:
        """随机获取一个模板类型"""

    @staticmethod
    def generate_opening(
        template_type: str,
        topic: str,
        philosopher: str = "",
        **kwargs
    ) -> str:
        """根据模板类型生成开头"""

    @staticmethod
    def generate_by_philosopher(
        philosopher: str,
        topic: str
    ) -> str:
        """根据哲学家推荐合适的开头类型"""
```

### 7.3 EndingGenerator

```python
class EndingGenerator:
    """互动结尾生成器"""

    @staticmethod
    def generate_interaction_ending(**kwargs) -> str:
        """生成互动结尾"""

    @staticmethod
    def generate_empathy_ending(**kwargs) -> str:
        """生成共情金句结尾"""

    @staticmethod
    def generate_twist_ending(**kwargs) -> str:
        """生成反转结尾"""

    @staticmethod
    def generate_full_ending(**kwargs) -> str:
        """生成完整的结尾三件套"""
```

---

## 八、未来优化方向

### 8.1 P1 优先级

- [ ] **爆点密度检测引擎**：每15-20秒必须一个爆点
- [ ] **多账号差异化风格**：技术流/治愈系/干货向
- [ ] **个人知识库RAG**：学习用户历史爆款风格

### 8.2 P2 优先级

- [ ] **周度作战图生成**：数据回流，自动优化
- [ ] **多平台风格适配**：抖音/B站/视频号
- [ ] **AB测试框架**：自动对比不同文案效果

---

## 九、附录

### 9.1 相关文档

- [工作流设计文档](./WORKFLOW-DESIGN.md)
- [系统设计文档](./DESIGN.md)
- [火山引擎API指南](./volcengine-ark-guide.md)

### 9.2 代码文件

| 文件 | 路径 | 说明 |
|-----|------|------|
| 语感适配器 | `app/style/xiaohongshu.py` | AI味检测、文案适配 |
| 模板库 | `app/style/templates.py` | 黄金三秒、结尾生成 |
| 文案节点 | `app/workflow/nodes/writer.py` | 集成新模块 |
| 模块导出 | `app/style/__init__.py` | 统一导出接口 |

---

**文档维护**: 本文档随代码更新同步维护，如有变更请及时更新。
