import json
from pathlib import Path

import pytest


from yspy.data_parsing.exceptions import DataParsingException
from yspy.data_parsing.search_result import ChannelComponent

TEST_DATAS = Path(__file__).parent / 'test_datas'


def load_fixture(name):
    with open(TEST_DATAS / name, encoding='utf-8') as f:
        return json.load(f)


def test_parse_channel_renderer():
    component = ChannelComponent.from_json(load_fixture('channel_renderer.json'))

    assert component.id == 'UCZRcA_nO3Kt-SOml2mY8D9g'
    assert component.title == 'test'
    assert component.url == 'https://youtube.com/@tutorialismic'
    assert component.subscribers_count_text == '264K subscribers'
    assert component.description_snippet.startswith('Get your own difficulty faces!')
    assert [(t.width, t.height) for t in component.thumbnails] == [(88, 88), (176, 176)]


def test_channel_component_from_invalid_data_raises():
    with pytest.raises(DataParsingException):
        ChannelComponent.from_json({'not_a_channel_renderer': {}})
