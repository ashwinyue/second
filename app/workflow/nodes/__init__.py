"""
工作流节点
"""
from .init import init_node
from .writer import writer_node
from .images import route_images_node, generate_image_node, aggregate_images_node
from .videos import route_videos_node, generate_video_node, aggregate_videos_node
from .compose import compose_node
from .audio import narrator_node, add_audio_node

__all__ = [
    "init_node",
    "writer_node",
    "route_images_node",
    "generate_image_node",
    "aggregate_images_node",
    "route_videos_node",
    "generate_video_node",
    "aggregate_videos_node",
    "compose_node",
    "narrator_node",
    "add_audio_node",
]

# 条件路由函数在 graph.py 中定义，不在这里导出
