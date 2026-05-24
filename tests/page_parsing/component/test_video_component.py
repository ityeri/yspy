import json
from pathlib import Path

from yspy.data_parsing.search_result import VideoComponent


with open(Path(__file__).parent / 'test_datas/video_renderer.json', 'r', encoding='utf-8') as f:
    test_video_renderer = json.load(f)

with open(Path(__file__).parent / 'test_datas/shorts_video_renderer.json', 'r', encoding='utf-8') as f:
    test_shorts_video_renderer = json.load(f)

video_component = VideoComponent.from_json(test_video_renderer)
shorts_video_component = VideoComponent.from_json(test_shorts_video_renderer)

breakpoint()