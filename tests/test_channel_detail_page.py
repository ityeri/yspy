import json
from pathlib import Path

from yspy.page_parsing import ChannelDetailPage

with open(Path(__file__).parent / 'test_datas/full_page/test_channel_detail_page.json', 'r') as f:
    raw_data = json.load(f)

channel_detail_page = ChannelDetailPage.from_json(raw_data)

breakpoint()
