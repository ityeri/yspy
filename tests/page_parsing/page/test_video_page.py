import json
from pathlib import Path

import pytest

TEST_DATAS = Path(__file__).parent / 'test_datas'


def load_fixture(name):
    with open(TEST_DATAS / name, encoding='utf-8') as f:
        return json.load(f)


from yspy.data_parsing.exceptions import DataParsingException
from yspy.data_parsing.player import PlayerPage, PlayerState


def test_parse_player_page():
    # the fixture carries videoDetails + microformat but no playabilityStatus
    page, state = PlayerPage.from_json(load_fixture('player_page.json'))

    assert page is not None
    assert state == PlayerState.UNKNOWN
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


def test_player_page_of_ok_video_without_microformat():
    # pot-free clients (e.g. visionos) answer OK but omit microformat —
    # the state is still reported while the full page stays unavailable
    page, state = PlayerPage.from_json(load_fixture('player_page_ok.json'))

    assert page is None
    assert state == PlayerState.OK
    assert state.value == 'OK'


def test_player_page_of_unavailable_video():
    page, state = PlayerPage.from_json(load_fixture('player_page_unavailable.json'))

    assert page is None
    assert state == PlayerState.ERROR


def test_player_page_of_login_required_video():
    page, state = PlayerPage.from_json(load_fixture('player_page_login.json'))

    assert page is None
    assert state == PlayerState.LOGIN_REQUIRED


def test_player_page_of_live_recording():
    # the recording of a live stream: videoDetails present, not playable
    page, state = PlayerPage.from_json(load_fixture('player_page_live_recording.json'))

    assert page is None
    assert state == PlayerState.UNPLAYABLE


def test_player_page_of_unrelated_data_raises():
    with pytest.raises(DataParsingException):
        PlayerPage.from_json({'unrelated': 1})


def test_player_page_state_parsing_from_status_tokens():
    assert PlayerState('OK') is PlayerState.OK
    assert PlayerState('LOGIN_REQUIRED') is PlayerState.LOGIN_REQUIRED
    assert PlayerState('LIVE_STREAM_OFFLINE') is PlayerState.LIVE_STREAM_OFFLINE
