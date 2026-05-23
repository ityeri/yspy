import json
from pathlib import Path

from yspy.page_parsing import VideNextPage

with open(Path(__file__).parent / 'test_datas/continuation_video_page.json', 'r', encoding='utf-8') as f:
    raw_data = json.load(f)

continuation_video_page = VideNextPage.from_json(raw_data)

breakpoint()
