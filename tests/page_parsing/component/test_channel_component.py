import json
from pathlib import Path

from yspy.data_parsing.search_result import ChannelComponent

with open(Path(__file__).parent / 'test_datas/channel_renderer.json', 'r', encoding='utf-8') as f:
    test_data = json.load(f)

component = ChannelComponent.from_json(test_data)
breakpoint()