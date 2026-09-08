import pytest

from yspy.api.video import Video, VideoUnavailableState
from yspy.data_parsing.player import PlayerAvailability, PlayerState


@pytest.mark.parametrize(
    ('state', 'reason', 'expected'),
    [
        # UNPLAYABLE — members-only wording variants seen in the wild
        (
            PlayerState.UNPLAYABLE,
            'Join this channel from your computer or mobile app to get access '
            'to members-only content like this video.',
            VideoUnavailableState.MEMBERS_ONLY,
        ),
        (
            PlayerState.UNPLAYABLE,
            'Join this channel to get access to members-only content like this '
            'video, and other exclusive perks.',
            VideoUnavailableState.MEMBERS_ONLY,
        ),
        (
            PlayerState.UNPLAYABLE,
            'This live stream recording is not available.',
            VideoUnavailableState.RECORDING_UNAVAILABLE,
        ),
        (
            PlayerState.UNPLAYABLE,
            'Sign in to your primary account to confirm your age.',
            VideoUnavailableState.AGE_RESTRICTED,
        ),
        (
            PlayerState.UNPLAYABLE,
            'The uploader has not made this video available in your country',
            VideoUnavailableState.REGION_BLOCKED,
        ),
        (
            PlayerState.UNPLAYABLE,
            'This video contains content from X, who has blocked it in your '
            'country on copyright grounds',
            VideoUnavailableState.COPYRIGHT_BLOCKED,
        ),
        (
            PlayerState.UNPLAYABLE,
            'Some unknown unplayable reason',
            VideoUnavailableState.UNAVAILABLE,
        ),
        # LOGIN_REQUIRED
        (
            PlayerState.LOGIN_REQUIRED,
            "Sign in to confirm you're not a bot",
            VideoUnavailableState.BOT_DETECTION,
        ),
        (
            PlayerState.LOGIN_REQUIRED,
            'Sign in to confirm your age',
            VideoUnavailableState.AGE_RESTRICTED,
        ),
        (
            PlayerState.LOGIN_REQUIRED,
            'Sign in to watch this video',
            VideoUnavailableState.LOGIN_REQUIRED,
        ),
        # AGE_CHECK_REQUIRED
        (
            PlayerState.AGE_CHECK_REQUIRED,
            'Age-restricted video',
            VideoUnavailableState.AGE_RESTRICTED,
        ),
        # ERROR
        (
            PlayerState.ERROR,
            'This video is private',
            VideoUnavailableState.PRIVATE,
        ),
        (
            PlayerState.ERROR,
            'This video has been removed by the uploader',
            VideoUnavailableState.REMOVED_BY_UPLOADER,
        ),
        (
            PlayerState.ERROR,
            'This account associated with this video has been terminated.',
            VideoUnavailableState.ACCOUNT_TERMINATED,
        ),
        (
            PlayerState.ERROR,
            'This video has been removed for violating YouTube Community Guidelines.',
            VideoUnavailableState.REMOVED_FOR_TOS,
        ),
        (
            PlayerState.ERROR,
            'This video is unavailable',
            VideoUnavailableState.UNAVAILABLE,
        ),
        (
            PlayerState.LIVE_STREAM_OFFLINE,
            'This live event has ended.',
            VideoUnavailableState.UNAVAILABLE,
        ),
    ],
)
def test_classify_unavailability(state, reason, expected):
    availability = PlayerAvailability(state, reason)
    assert Video._classify_unavailability(availability) is expected


def test_available_states_are_not_unavailable():
    assert Video._is_unavailable(PlayerAvailability(PlayerState.OK)) is False
    assert Video._is_unavailable(PlayerAvailability(PlayerState.LIVE_STREAM)) is False
    assert Video._is_unavailable(PlayerAvailability(PlayerState.UNKNOWN)) is False


def test_unavailable_states_are_unavailable():
    for state in (
            PlayerState.UNPLAYABLE,
            PlayerState.LOGIN_REQUIRED,
            PlayerState.AGE_CHECK_REQUIRED,
            PlayerState.ERROR,
            PlayerState.LIVE_STREAM_OFFLINE,
    ):
        assert Video._is_unavailable(PlayerAvailability(state)) is True
