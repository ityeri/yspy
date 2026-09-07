import json
from pathlib import Path

import pytest


from yspy.data_parsing.exceptions import DataParsingException
from yspy.data_parsing.search_result import VideoComponent

TEST_DATAS = Path(__file__).parent / 'test_datas'


def load_fixture(name):
    with open(TEST_DATAS / name, encoding='utf-8') as f:
        return json.load(f)


def test_parse_video_renderer():
    component = VideoComponent.from_json(load_fixture('video_renderer.json'))

    assert component.id == 'F6EldAIgOMc'
    assert component.title == 'Wonderful OLED TEST 16K Video | Dolby Vision HDR 120FPS (8K/4K Video TV)'
    assert component.url.startswith('https://youtube.com/watch?v=F6EldAIgOMc')
    assert component.is_shorts is False
    assert component.published_time_text == '1 day ago'
    assert component.length_text == '1:01:16'
    assert component.view_count_text == '20,782 views'
    assert component.channel_url == 'https://youtube.com/@12KVIDEOULTRAHD.'
    assert component.channel_id == 'UCe4A97DMN-5zPaxnS-TqN_w'
    assert [(t.width, t.height) for t in component.thumbnails] == [(360, 202), (720, 404)]


def test_parse_shorts_video_renderer():
    component = VideoComponent.from_json(load_fixture('shorts_video_renderer.json'))

    assert component.id == 'plKc6fXYMTE'
    assert component.url.startswith('https://youtube.com/shorts/plKc6fXYMTE')
    assert component.is_shorts is True
    assert component.channel_id == 'UCBSem0KlPhoPK5M8cZWCS4w'


def test_video_component_from_invalid_data_raises():
    with pytest.raises(DataParsingException):
        VideoComponent.from_json({'not_a_video_renderer': {}})
