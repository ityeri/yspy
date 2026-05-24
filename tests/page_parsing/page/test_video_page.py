import json
from pathlib import Path

from yspy.data_parsing.video import VideoPage

with open(Path(__file__).parent / 'test_datas/video_page.json', 'r') as f:
    raw_data = json.load(f)

video_page_data = VideoPage.from_json(raw_data)

breakpoint()
