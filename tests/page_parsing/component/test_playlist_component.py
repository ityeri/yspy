import json
from pathlib import Path

import pytest


from yspy.data_parsing.exceptions import DataParsingException
from yspy.data_parsing.search_result import PlaylistComponent

TEST_DATAS = Path(__file__).parent / 'test_datas'


def load_fixture(name):
    with open(TEST_DATAS / name, encoding='utf-8') as f:
        return json.load(f)


def test_parse_playlist_lockup():
    component = PlaylistComponent.from_json(load_fixture('playlist_lockup.json'))

    assert component.id == 'PL_DD814i0-aIqCZe6S78WvbFvDB3E5y4z'
    assert component.title == '[LOL 롤] 리그 오브 레전드'
    assert component.url == 'https://youtube.com/playlist?list=PL_DD814i0-aIqCZe6S78WvbFvDB3E5y4z'
    assert component.channel_id == 'UCBvApW8Oem0ZaYEH9wIja5Q'
    assert component.channel_name == '메가게임 - Mega Game'
    assert len(component.thumbnails) == 1
    assert (component.thumbnails[0].width, component.thumbnails[0].height) == (480, 270)


def test_playlist_lockup_of_other_content_type_raises():
    with pytest.raises(DataParsingException):
        PlaylistComponent.from_json({'lockupViewModel': {'contentType': 'LOCKUP_CONTENT_TYPE_VIDEO'}})
