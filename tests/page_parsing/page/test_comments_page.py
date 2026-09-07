import json
from pathlib import Path

import pytest

TEST_DATAS = Path(__file__).parent / 'test_datas'


def load_fixture(name):
    with open(TEST_DATAS / name, encoding='utf-8') as f:
        return json.load(f)



from yspy.data_parsing import CommentsPage


def test_parse_comments_page():
    page = CommentsPage.from_json(load_fixture('continuation_comments_page.json'))

    assert len(page.comments) == 20
    assert isinstance(page.continuation_token, str) and len(page.continuation_token) > 50

    first = page.comments[0]
    assert first.author_display_name == '@허오키'
    assert first.comment.startswith('89299440분 저거 169.9년임ㅋㅋ')
