import json
from pathlib import Path

from yspy.data_parsing.channel import ChannelPage

with open(Path(__file__).parent / 'test_datas/channel_page.json', 'r', encoding='utf-8') as f:
    test_channel_page = json.load(f)

channel_page = ChannelPage.from_json(test_channel_page)

breakpoint()
