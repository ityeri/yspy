import json
from pathlib import Path

from yspy.page_parsing import ChannelPage

with open(Path(__file__).parent / 'test_datas/full_page/test_channel_page.json', 'r', encoding='utf-8') as f:
    test_channel_page = json.load(f)

channel_page = ChannelPage.from_json(test_channel_page)

breakpoint()
