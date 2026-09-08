import json
from pathlib import Path

TEST_DATAS = Path(__file__).parent / 'test_datas'


def load_fixture(name):
    with open(TEST_DATAS / name, encoding='utf-8') as f:
        return json.load(f)


from yspy.data_parsing.player import PlayerPage


def test_parse_player_page():
    page = PlayerPage.from_json(load_fixture('player_page.json'))

    assert page.id == 'z0GKGpObgPY'
    assert page.title == 'Harry Styles - Sign of the Times (Audio)'
    assert page.url == 'https://www.youtube.com/watch?v=z0GKGpObgPY'
    assert page.length_seconds == 342
    assert page.view_count == 177836495
    assert page.description.startswith('Official audio for')
    assert page.channel_id == 'UCbOCbp5gXL8jigIBZLqMPrw'
    assert page.channel_name == 'HarryStylesVEVO'
    assert page.is_live_content is False
    assert page.is_family_safe is True
    assert page.category == 'Music'
    assert len(page.thumbnails) == 5
