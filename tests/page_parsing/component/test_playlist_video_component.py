import json
from pathlib import Path

import pytest


from yspy.data_parsing.exceptions import DataParsingException
from yspy.data_parsing.playlist import PlaylistVideoComponent

TEST_DATAS = Path(__file__).parent / 'test_datas'


def load_fixture(name):
    with open(TEST_DATAS / name, encoding='utf-8') as f:
        return json.load(f)


def test_parse_playlist_video_lockup():
    component = PlaylistVideoComponent.from_json(load_fixture('playlist_video_lockup.json'), index=0)

    assert component.id == '6sFi_F3DJX4'
    assert component.title == '세상을 구하기 위해 떠나는 공룡서버 ㄷㄷㄷㄷㄷㄷㄷ'
    assert component.url == 'https://youtube.com/watch?v=6sFi_F3DJX4'
    assert component.index == 0
    assert component.owner_text == '각별'
    assert component.length_text == '21:34'
    assert len(component.thumbnails) == 4
    assert (component.thumbnails[0].width, component.thumbnails[0].height) == (168, 94)


def test_playlist_video_component_from_invalid_data_raises():
    with pytest.raises(DataParsingException):
        PlaylistVideoComponent.from_json({'not_a_lockup': {}}, index=0)
