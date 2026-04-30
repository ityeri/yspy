import json
from pathlib import Path

from yspy.page_parsing import PlaylistVideoComponent

with open(Path(__file__).parent / 'test_datas/component/test_playlist_video_renderer.json', 'r') as f:
    raw_data = json.load(f)

playlist_video_renderer = PlaylistVideoComponent.from_json(raw_data)

breakpoint()