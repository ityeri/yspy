import json
from pathlib import Path

import pytest

TEST_DATAS = Path(__file__).parent / 'test_datas'


def load_fixture(name):
    with open(TEST_DATAS / name, encoding='utf-8') as f:
        return json.load(f)



from yspy.data_parsing import VideoNextPage


def test_parse_video_next_page():
    page = VideoNextPage.from_json(load_fixture('continuation_video_page.json'))

    assert isinstance(page.comment_continuation_token, str) and len(page.comment_continuation_token) > 50
