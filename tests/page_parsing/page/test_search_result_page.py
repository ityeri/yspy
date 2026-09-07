import json
from pathlib import Path

import pytest

TEST_DATAS = Path(__file__).parent / 'test_datas'


def load_fixture(name):
    with open(TEST_DATAS / name, encoding='utf-8') as f:
        return json.load(f)



from yspy.data_parsing.search_result import SearchResultPage, VideoComponent, PlaylistComponent, ChannelComponent


def test_parse_first_search_result_page():
    page = SearchResultPage.from_json(load_fixture('search_result_page.json'))

    assert len(page.components) == 30
    assert all(isinstance(component, VideoComponent) for component in page.components)
    assert isinstance(page.continuation_token, str) and len(page.continuation_token) > 50

    first = page.components[0]
    assert first.id == 'OegyYwm6rqE'
    assert first.title.startswith('【BGM】Top 50 Most Popular Songs by NCS')
    assert first.view_count_text == '9,553,170 views'
    assert first.channel_id == 'UCwwtUfy0-CqN50HfaFDzL0w'
    assert page.components[-1].id  # non-empty


def test_parse_search_result_continuation_page():
    page = SearchResultPage.from_json(load_fixture('search_result_continuation_page.json'))

    assert len(page.components) == 20
    assert sum(isinstance(c, VideoComponent) for c in page.components) == 19
    assert sum(isinstance(c, PlaylistComponent) for c in page.components) == 1
    assert isinstance(page.continuation_token, str) and len(page.continuation_token) > 50


def test_parse_search_result_playlist_page():
    page = SearchResultPage.from_json(load_fixture('search_result_playlist_page.json'))

    assert len(page.components) == 20
    assert all(isinstance(component, PlaylistComponent) for component in page.components)

    first = page.components[0]
    assert first.id == 'PL_DD814i0-aIqCZe6S78WvbFvDB3E5y4z'
    assert first.title == '[LOL 롤] 리그 오브 레전드'
    assert first.channel_name == '메가게임 - Mega Game'


def test_parse_search_result_playlist_continuation_page():
    page = SearchResultPage.from_json(load_fixture('search_result_playlist_continuation_page.json'))

    assert len(page.components) == 20
    assert all(isinstance(component, PlaylistComponent) for component in page.components)
    assert isinstance(page.continuation_token, str) and len(page.continuation_token) > 50
