import json
from pathlib import Path

from yspy.page_parsing import PlaylistPage

with open(Path(__file__).parent / 'test_datas/playlist_page.json', 'r') as f:
    raw_playlist_page_data = json.load(f)
with open(Path(__file__).parent / 'test_datas/playlist_continuation_page.json', 'r') as f:
    raw_continuation_page_data = json.load(f)

playlist_page = PlaylistPage.from_json(raw_playlist_page_data)
continuation_page = PlaylistPage.from_json(raw_continuation_page_data)

breakpoint()