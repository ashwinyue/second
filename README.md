# DEAR Agent

**DEAR** = **D**igital **E**nlightenment & **A**rtistic **R**easoning（数字启蒙与艺术推理）

基于 LangGraph 的哲学科普视频生成 Agent，工作流：**文案 → 图像 → 视频 → 配音**

## 特性

- **流式实时进度**：使用 SSE (Server-Sent Events) 返回实时生成进度
- **并发处理**：LangGraph Send 接口实现图像/视频并发生成
- **风格一致性**：统一 seed + prompt 模板确保视觉风格统一
- **极简线条画风格**：火柴人角色、高饱和色块、扁平化设计

## 架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        FastAPI Web 层                          │
│  ┌────────────┐  ┌────────────┐                                │
│  │ SSE API    │  │  Static    │                                │
│  │ /api/v1/   │  │  /outputs  │                                │
│  └─────┬──────┘  └─────┬──────┘                                │
└────────┼──────────────────┼─────────────────────────────────────┘
         │ SSE 流           │ 静态文件
         ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                    LangGraph 工作流层                           │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                   StateGraph                              │  │
│  │   init → writer → images → videos → compose → narrator    │  │
│  └───────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────┬─────────────────────────┘
                                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                        服务层（火山引擎）                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │   LLM    │  │  Image   │  │  Video   │  │   TTS    │      │
│  │ doubao   │  │seedream  │  │seedance  │  │WebSocket │      │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘      │
└─────────────────────────────────────────────────────────────────┘
```

## 技术栈

### 后端
- **FastAPI** - Python Web 框架
- **LangGraph** - 工作流编排
- **LangChain** - LLM 集成
- **火山引擎** - AI 服务（豆包 LLM、文生图、视频生成、TTS）

### 前端
- **React 18** + TypeScript + Vite
- **Radix UI** + Tailwind CSS
- 原生 fetch + SSE 流式接收

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- FFmpeg

### 后端设置

```bash
# 1. 安装依赖
pip install uv
uv pip install -e .

# 2. 配置环境变量（参考 .env.example）
cp .env.example .env

# 3. 启动服务
./run_server.sh
```

### 前端设置

```bash
cd web
npm install
npm run dev
```

## API 端点

| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/v1/generate` | POST | SSE 流式生成视频 |
| `/api/v1/health` | GET | 健康检查 |
| `/outputs/final/{filename}` | GET | 获取视频文件 |

## SSE 事件类型

| 事件 | 数据 | 说明 |
|------|------|------|
| `init` | `{task_id, topic}` | 任务初始化 |
| `progress` | `{step, progress, message}` | 进度更新 |
| `scene` | `{scene_id, type, url}` | 图片/视频生成完成 |
| `done` | `{final_video_url}` | 完成 |
| `error` | `{message}` | 错误 |

## 项目结构

```
second/
├── app/                      # Python 包
│   ├── state.py              # LangGraph 状态
│   ├── config.py             # 配置管理
│   ├── style.py              # 风格管理
│   ├── graph.py              # LangGraph 工作流
│   ├── nodes/                # 节点函数
│   ├── services/             # 外部服务
│   └── api/                  # FastAPI 层
├── outputs/                  # 生成结果
├── web/                      # React 前端
├── docs/                     # 文档
├── pyproject.toml
└── .env.example
```

## 并发策略

| API | 并发支持 | 策略 |
|-----|---------|------|
| 文生图 | ✅ | Semaphore=5, 统一 seed |
| 视频生成 | ✅ | Semaphore=3, 异步轮询 |
| LLM | ✅ | 标准调用 |
| TTS | - | WebSocket 串行处理 |

## 开发

```bash
# 运行测试
pytest

# 代码格式化
ruff format .

# 代码检查
ruff check .
```

## 文档

- [设计文档](./docs/DESIGN.md)
- [工作流设计](./docs/WORKFLOW-DESIGN.md)
- [火山引擎指南](./docs/volcengine-ark-guide.md)

## License

MIT
