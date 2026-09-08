import json
from pathlib import Path

import pytest

TEST_DATAS = Path(__file__).parent / 'test_datas'


def load_fixture(name):
    with open(TEST_DATAS / name, encoding='utf-8') as f:
        return json.load(f)


from yspy.data_parsing.exceptions import DataParsingException
from yspy.data_parsing.player import PlayerAvailability, PlayerPage, PlayerState


def test_parse_player_page():
    # the fixture carries videoDetails + microformat but no playabilityStatus
    page, availability = PlayerPage.from_json(load_fixture('player_page.json'))

    assert page is not None
    assert availability.state == PlayerState.UNKNOWN
    assert availability.reason is None
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
    page, availability = PlayerPage.from_json(load_fixture('player_page_ok.json'))

    assert page is None
    assert availability.state == PlayerState.OK
    assert availability.state.value == 'OK'
    assert availability.reason is None


def test_player_page_of_unavailable_video():
    page, availability = PlayerPage.from_json(load_fixture('player_page_unavailable.json'))

    assert page is None
    assert availability.state == PlayerState.ERROR
    assert availability.reason == 'This video is unavailable'


def test_player_page_of_login_required_video():
    page, availability = PlayerPage.from_json(load_fixture('player_page_login.json'))

    assert page is None
    assert availability.state == PlayerState.LOGIN_REQUIRED
    assert 'not a bot' in availability.reason


def test_player_page_of_live_recording():
    # the recording of a live stream: videoDetails present, not playable
    page, availability = PlayerPage.from_json(load_fixture('player_page_live_recording.json'))

    assert page is None
    assert availability.state == PlayerState.UNPLAYABLE
    assert availability.reason == 'This live stream recording is not available.'


def test_player_page_of_members_only_video():
    # members-only: videoDetails present but partial (no view_count) and
    # microformat present — the page cannot be built but the verdict stays
    page, availability = PlayerPage.from_json(load_fixture('player_page_members.json'))

    assert page is None
    assert availability.state == PlayerState.UNPLAYABLE
    assert availability.reason == (
        'Join this channel from your computer or mobile app to get access '
        'to members-only content like this video.'
    )


def test_player_page_of_unrelated_data_raises():
    with pytest.raises(DataParsingException):
        PlayerPage.from_json({'unrelated': 1})


def test_player_page_state_parsing_from_status_tokens():
    assert PlayerState('OK') is PlayerState.OK
    assert PlayerState('LOGIN_REQUIRED') is PlayerState.LOGIN_REQUIRED
    assert PlayerState('LIVE_STREAM_OFFLINE') is PlayerState.LIVE_STREAM_OFFLINE
