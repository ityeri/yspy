import json
from pathlib import Path

TEST_DATAS = Path(__file__).parent / 'test_datas'


def load_fixture(name):
    with open(TEST_DATAS / name, encoding='utf-8') as f:
        return json.load(f)


from yspy.data_parsing.player import PlayerNextPage


def test_parse_player_next_page():
    page = PlayerNextPage.from_json(load_fixture('player_next_page.json'))

    assert isinstance(page.comment_continuation_token, str) and len(page.comment_continuation_token) > 50
