import json
from pathlib import Path

from yspy.page_parsing import PlaylistPage

with open(Path(__file__).parent / 'test_datas/playlist_page.json', 'r') as f:
    raw_data = json.load(f)


playlist_page = PlaylistPage.from_json(raw_data)

breakpoint()