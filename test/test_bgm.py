"""
测试背景音乐功能
"""
import asyncio
import logging
from pathlib import Path

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_background_music():
    """测试背景音乐配置"""
    from app.config import get_settings
    from app.workflow.nodes.audio import _get_background_music

    settings = get_settings()

    print("=" * 50)
    print("背景音乐配置测试")
    print("=" * 50)

    # 显示配置
    print(f"\n📋 当前配置:")
    print(f"  - BGM_ENABLED: {settings.bgm_enabled}")
    print(f"  - BGM_VOLUME: {settings.bgm_volume}")

    # 获取背景音乐
    bgm_path = _get_background_music()

    print(f"\n🎵 背景音乐文件:")
    if bgm_path and Path(bgm_path).exists():
        print(f"  ✓ 文件路径: {bgm_path}")
        print(f"  ✓ 文件大小: {Path(bgm_path).stat().st_size / 1024 / 1024:.2f} MB")

        # 列出所有可用音乐
        bgm_dir = Path(bgm_path).parent
        music_files = list(bgm_dir.glob("*.mp3"))
        print(f"\n📁 可用背景音乐列表 ({len(music_files)} 首):")
        for i, f in enumerate(music_files, 1):
            size_mb = f.stat().st_size / 1024 / 1024
            print(f"  {i}. {f.name} ({size_mb:.2f} MB)")
    else:
        print(f"  ✗ 未找到背景音乐文件")

    print("\n" + "=" * 50)
    print("测试完成!")
    print("=" * 50)


async def test_ffmpeg_audio_mix():
    """测试 FFmpeg 音频混合功能"""
    import subprocess
    import tempfile

    print("\n🎬 测试 FFmpeg 音频混合功能...")

    # 检查 FFmpeg 是否可用
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        print("  ✓ FFmpeg 可用")
    except Exception as e:
        print(f"  ✗ FFmpeg 不可用: {e}")
        return

    # 测试音频滤镜
    bgm_path = _get_background_music()
    if not bgm_path or not Path(bgm_path).exists():
        print("  ✗ 跳过测试（无背景音乐文件）")
        return

    # 创建测试输出文件
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        output_path = f.name

    try:
        # 测试音量调整和循环滤镜
        cmd = [
            "ffmpeg",
            "-i", bgm_path,
            "-filter_complex", f"[0:a]volume=0.2,aloop=loop=-1:size=2e+09[audioout]",
            "-map", "[audioout]",
            "-t", "5",  # 只输出 5 秒用于测试
            "-y",
            output_path
        ]

        print(f"  执行命令: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            print(f"  ✓ 音频滤镜测试成功")
        else:
            print(f"  ✗ 音频滤镜测试失败: {result.stderr}")

    finally:
        # 清理临时文件
        Path(output_path).unlink(missing_ok=True)


if __name__ == "__main__":
    asyncio.run(test_background_music())
    asyncio.run(test_ffmpeg_audio_mix())
