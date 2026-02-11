# 背景音乐功能说明

## 📖 功能概述

视频生成流程现已支持自动添加背景音乐。背景音乐会在最终视频合成阶段与人声配音自动混合，音量经过优化以确保不干扰人声。

## 🎵 已安装的背景音乐

项目已预装 5 首免费可商用的背景音乐，位于 `assets/bgm/` 目录：

| 音乐名称 | 风格 | 时长 | 适用场景 |
|---------|------|------|---------|
| Ambient Background 2 | 环境音乐 | 3:13 | 情感叙述、知识分享 |
| Cinematic Ambient | 电影氛围 | 2:08 | 深度内容、品牌宣传 |
| Emotional Ambient | 情感音乐 | 2:12 | 情感共鸣强的内容 |
| Upbeat Music | 轻快风格 | 1:53 | 小红书风格、生活分享 |
| Energetic Upbeat | 活力动感 | 2:00 | 快节奏、产品展示 |

## ⚙️ 配置选项

在 `.env` 文件中添加以下配置：

```bash
# 背景音乐配置
BGM_ENABLED=true          # 是否启用背景音乐 (true/false)
BGM_VOLUME=0.2            # 背景音乐音量 (0.0-1.0)，建议 0.15-0.25
```

### 配置说明

- **BGM_ENABLED**: 控制是否使用背景音乐
  - `true`: 启用背景音乐（默认）
  - `false`: 禁用背景音乐

- **BGM_VOLUME**: 背景音乐的音量比例
  - 范围: 0.0（静音）到 1.0（原音量）
  - 推荐值: 0.15-0.25（15%-25%）
  - 默认值: 0.2

## 🔧 技术实现

### 工作流程

```
视频合成 → TTS配音 → 音频混合（含背景音乐）→ 最终视频
```

### FFmpeg 音频处理

背景音乐通过以下 FFmpeg 滤镜处理：

1. **音量调整**: 使用 `volume` 滤镜降低背景音乐音量
2. **音频循环**: 使用 `aloop` 滤镜循环播放背景音乐以匹配视频长度
3. **音频混合**: 使用 `amix` 滤镜将人声和背景音乐混合

### 关键代码位置

- **配置**: `app/config.py` - `Settings` 类中的 `bgm_enabled` 和 `bgm_volume`
- **音频节点**: `app/workflow/nodes/audio.py` - `add_audio_node` 函数
- **音乐选择**: `app/workflow/nodes/audio.py` - `_get_background_music` 函数

## 📦 添加更多音乐

将 MP3/WAV/M4A 等格式的音乐文件放入 `assets/bgm/` 目录即可。系统会随机选择一首作为背景音乐。

### 推荐资源

- [Pixabay Music](https://pixabay.com/music/) - 22万+ 免费音乐
- [No Copyright Music](https://www.no-copyright-music.com/) - 现代无版权音乐
- [Free Music Archive](https://freemusicarchive.org/) - 高质量策展音乐

## 🎯 使用建议

### 音量设置指南

| 内容类型 | 背景音乐音量 | 说明 |
|---------|-------------|------|
| 纯音乐视频 | 0.3-0.4 | 音乐作为主要内容 |
| 叙述/讲解 | 0.15-0.2 | 确保人声清晰 |
| 情感类内容 | 0.2-0.25 | 音乐烘托氛围 |

### 音乐风格选择

| 内容风格 | 推荐音乐类型 |
|---------|-------------|
| 小红书/抖音 | Upbeat（轻快） |
| 知识分享 | Ambient（环境音乐） |
| 品牌宣传 | Cinematic（电影感） |
| 情感故事 | Emotional（情感音乐） |

## 📄 授权信息

所有预装背景音乐均来自 [Pixabay](https://pixabay.com/music/)，遵循 Pixabay Content License：
- ✅ 可用于商业项目
- ✅ 无需署名（但建议署名）
- ✅ 可修改和混音
- ✅ 可在线发布和分发
