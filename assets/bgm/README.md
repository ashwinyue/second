# 背景音乐资源库

本目录包含免费可商用的背景音乐，用于视频配音。

## 音乐列表

### 1. Ambient Background 2
- **文件**: `delosound-ambient-background-2-421085.mp3`
- **时长**: 3:13
- **风格**: Ambient Background（环境背景音乐）
- **作者**: DELOSound
- **来源**: [Pixabay](https://pixabay.com/music/ambient-ambient-background-2-421085/)
- **特点**: 轻柔、舒缓，适合情感类、叙述类视频

### 2. Cinematic Ambient
- **文件**: `tunetank-cinematic-ambient-348342.mp3`
- **时长**: 2:08
- **风格**: Cinematic Ambient（电影感环境音乐）
- **作者**: Tunetank
- **来源**: [Pixabay](https://pixabay.com/music/small-drama-cinematic-ambient-348342/)
- **特点**: 大气、有层次感，适合内容深度较高的视频

### 3. Emotional Ambient
- **文件**: `audiodollar-ambient-emotional-ambient-451321.mp3`
- **时长**: 2:12
- **风格**: Ambient Emotional（情感环境音乐）
- **作者**: AudioDollar
- **来源**: [Pixabay](https://pixabay.com/music/ambient-ambient-emotional-ambient-451321/)
- **特点**: 温暖、感性，适合情感共鸣强的内容

### 4. Upbeat Music
- **文件**: `lnplusmusic-upbeat-music-469480.mp3`
- **时长**: 1:53
- **风格**: Upbeat（轻快音乐）
- **作者**: lNPLUSMUSIC
- **来源**: [Pixabay](https://pixabay.com/music/upbeat-upbeat-music-469480/)
- **特点**: 活力、积极，适合小红书风格的轻快内容

### 5. Energetic Upbeat Background
- **文件**: `tatamusic-energetic-upbeat-background-music-377668.mp3`
- **时长**: 2:00
- **风格**: Energetic Upbeat（活力轻快）
- **作者**: Tatamusic
- **来源**: [Pixabay](https://pixabay.com/music/upbeat-energetic-upbeat-background-music-377668/)
- **特点**: 充满能量、动感，适合节奏较快的内容

## 使用说明

### 授权信息
所有音乐均来自 [Pixabay](https://pixabay.com/music/)，遵循 Pixabay Content License：
- ✅ 可用于商业项目
- ✅ 无需署名（但建议署名）
- ✅ 可修改和混音
- ✅ 可在线发布和分发

### 建议音量设置
背景音乐应降低音量以免干扰人声：
- **音乐音量**: 15-25%
- **人声音量**: 100%

### 推荐使用场景
| 音乐类型 | 适用场景 |
|---------|---------|
| Ambient 系列 | 情感叙述、知识分享、深度内容 |
| Upbeat 系列 | 产品展示、生活方式、快节奏内容 |
| Cinematic | 品牌宣传、高质量视觉内容 |

## 获取更多音乐

### 推荐资源平台

#### 免费可商用
- **[Pixabay Music](https://pixabay.com/music/)** - 22万+免费音乐，无需注册
- **[No Copyright Music](https://www.no-copyright-music.com/)** - 现代无版权音乐
- **[Free Music Archive](https://freemusicarchive.org/)** - 高质量策展音乐
- **[Chosic](https://www.chosic.com/free-music/)** - 适合YouTube和社交媒体

#### 需署名的免费资源
- **[Bensound](https://www.bensound.com/royalty-free-music)** - 高质量音乐，需注明来源
- **[Uppbeat](https://uppbeat.io/)** - 专业音乐库，免费版需署名

#### 中文平台
- **[耳聆网](https://www.erailing.com/)** - 国内音频素材社区
- **[淘声网](https://www.tosound.com/)** - 免费音效和背景音乐

### 搜索关键词建议
- `ambient background` - 环境背景音乐
- `upbeat instrumental` - 轻快纯音乐
- `cinematic` - 电影感音乐
- `corporate` - 商务风格
- `inspiring` - 励志风格

## 技术说明

### 音乐格式
- **格式**: MP3
- **采样率**: 44.1 kHz 或更高
- **比特率**: 128-320 kbps

### 代码集成示例

```python
# 在视频合成时添加背景音乐
from moviepy.editor import AudioFileClip, CompositeAudioClip

def add_background_music(video_path, music_path, output_path, music_volume=0.2):
    video = VideoFileClip(video_path)
    music = AudioFileClip(music_path)

    # 循环音乐以匹配视频长度
    music = music.loop(duration=video.duration)

    # 降低音乐音量
    music = music.volumex(music_volume)

    # 混合音频
    final_audio = CompositeAudioClip([video.audio, music])
    final_video = video.set_audio(final_audio)
    final_video.write_videofile(output_path)
```
