import pytest

from yspy.api.video import Video, VideoState
from yspy.data_parsing.player import PlayerAvailability, PlayerState


@pytest.mark.parametrize(
    ('state', 'reason', 'expected'),
    [
        # available states collapse to OK
        (PlayerState.OK, None, VideoState.OK),
        (PlayerState.LIVE_STREAM, 'This is a live stream.', VideoState.OK),
        (PlayerState.UNKNOWN, None, VideoState.OK),
        # UNPLAYABLE — members-only wording variants seen in the wild
        (
            PlayerState.UNPLAYABLE,
            'Join this channel from your computer or mobile app to get access '
            'to members-only content like this video.',
            VideoState.MEMBERS_ONLY,
        ),
        (
            PlayerState.UNPLAYABLE,
            'Join this channel to get access to members-only content like this '
            'video, and other exclusive perks.',
            VideoState.MEMBERS_ONLY,
        ),
        (
            PlayerState.UNPLAYABLE,
            'This live stream recording is not available.',
            VideoState.RECORDING_UNAVAILABLE,
        ),
        (
            PlayerState.UNPLAYABLE,
            'Sign in to your primary account to confirm your age.',
            VideoState.AGE_RESTRICTED,
        ),
        (
            PlayerState.UNPLAYABLE,
            'The uploader has not made this video available in your country',
            VideoState.REGION_BLOCKED,
        ),
        (
            PlayerState.UNPLAYABLE,
            'This video contains content from X, who has blocked it in your '
            'country on copyright grounds',
            VideoState.COPYRIGHT_BLOCKED,
        ),
        (
            PlayerState.UNPLAYABLE,
            'Some unknown unplayable reason',
            VideoState.UNAVAILABLE,
        ),
        # LOGIN_REQUIRED
        (
            PlayerState.LOGIN_REQUIRED,
            "Sign in to confirm you're not a bot",
            VideoState.BOT_DETECTION,
        ),
        (
            PlayerState.LOGIN_REQUIRED,
            'Sign in to confirm your age',
            VideoState.AGE_RESTRICTED,
        ),
        (
            PlayerState.LOGIN_REQUIRED,
            'Sign in to watch this video',
            VideoState.LOGIN_REQUIRED,
        ),
        # AGE_CHECK_REQUIRED
        (
            PlayerState.AGE_CHECK_REQUIRED,
            'Age-restricted video',
            VideoState.AGE_RESTRICTED,
        ),
        # ERROR
        (
            PlayerState.ERROR,
            'This video is private',
            VideoState.PRIVATE,
        ),
        (
            PlayerState.ERROR,
            'This video has been removed by the uploader',
            VideoState.REMOVED_BY_UPLOADER,
        ),
        (
            PlayerState.ERROR,
            'This account associated with this video has been terminated.',
            VideoState.ACCOUNT_TERMINATED,
        ),
        (
            PlayerState.ERROR,
            'This video has been removed for violating YouTube Community Guidelines.',
            VideoState.REMOVED_FOR_TOS,
        ),
        (
            PlayerState.ERROR,
            'This video is unavailable',
            VideoState.UNAVAILABLE,
        ),
        (
            PlayerState.LIVE_STREAM_OFFLINE,
            'This live event has ended.',
            VideoState.UNAVAILABLE,
        ),
    ],
)
def test_get_video_state(state, reason, expected):
    availability = PlayerAvailability(state, reason)
    assert Video._get_video_state(availability) is expected

