import json
from pathlib import Path

from yspy.data_parsing.playlist import PlaylistVideoComponent

with open(Path(__file__).parent / 'test_datas/playlist_video_renderer.json', 'r') as f:
    raw_data = json.load(f)

playlist_video_renderer = PlaylistVideoComponent.from_json(raw_data)

breakpoint()