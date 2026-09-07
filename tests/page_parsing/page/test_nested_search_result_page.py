import json
from pathlib import Path

import pytest

TEST_DATAS = Path(__file__).parent / 'test_datas'


def load_fixture(name):
    with open(TEST_DATAS / name, encoding='utf-8') as f:
        return json.load(f)



from yspy.data_parsing.search_result import SearchResultPage, VideoComponent, PlaylistComponent


def test_parse_nested_search_result_page():
    # search results where a shelf holds nested components (videos and a playlist lockup)
    page = SearchResultPage.from_json(load_fixture('nested_search_result.json'))

    assert len(page.components) == 14
    assert sum(isinstance(c, VideoComponent) for c in page.components) == 13
    assert sum(isinstance(c, PlaylistComponent) for c in page.components) == 1
    assert isinstance(page.continuation_token, str) and len(page.continuation_token) > 50

    assert page.components[0].id == 'kijpcUv-b8M'
    assert page.components[0].title == 'Queen - Somebody To Love (Official Video)'
