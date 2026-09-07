import json
from pathlib import Path

import pytest

TEST_DATAS = Path(__file__).parent / 'test_datas'


def load_fixture(name):
    with open(TEST_DATAS / name, encoding='utf-8') as f:
        return json.load(f)



from yspy.data_parsing.playlist import PlaylistPage


def test_parse_playlist_first_page():
    page = PlaylistPage.from_json(load_fixture('playlist_page.json'))

    assert page.id == 'UUDrAR1OWC2MD4s0JLetN0MA'
    assert page.title == 'Uploads from 각별'
    assert page.owner_text == '각별'
    assert page.owner_id == 'UCDrAR1OWC2MD4s0JLetN0MA'
    assert page.view_count_text == '1,692,286 views'
    assert len(page.videos) == 100
    assert isinstance(page.continuation_token, str) and len(page.continuation_token) > 50

    first = page.videos[0]
    assert first.id == '6sFi_F3DJX4'
    assert first.index == 0
    assert first.owner_text == '각별'


def test_parse_playlist_continuation_page():
    page = PlaylistPage.from_json(load_fixture('playlist_continuation_page.json'))

    assert len(page.videos) == 100
    assert page.continuation_token is None  # last page

    first = page.videos[0]
    assert first.id == 'EGSk5OrgAzU'
    assert first.index == 0
