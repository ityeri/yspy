from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from yspy.utils import get_by_path, get_by_path_or
from ..exceptions import DataParsingException
from ..image_component import ImageComponent


class PlayerState(str, Enum):
    # states mirror the playabilityStatus.status tokens of the player response
    OK = 'OK'
    UNPLAYABLE = 'UNPLAYABLE'
    LOGIN_REQUIRED = 'LOGIN_REQUIRED'
    AGE_CHECK_REQUIRED = 'AGE_CHECK_REQUIRED'
    LIVE_STREAM = 'LIVE_STREAM'
    LIVE_STREAM_OFFLINE = 'LIVE_STREAM_OFFLINE'
    ERROR = 'ERROR'
    UNKNOWN = 'UNKNOWN'


@dataclass(frozen=True)
class PlayerAvailability:
    # the availability verdict of a player response: the state plus the reason
    # the player gave (e.g. 'Join this channel ... members-only content')
    state: PlayerState
    reason: str | None = None


@dataclass
class PlayerPage:
    id: str
    title: str
    url: str
    length_seconds: int
    view_count: int
    thumbnails: list[ImageComponent]
    description: str
    channel_id: str
    channel_name: str
    is_live_content: bool
    publish_date: datetime
    upload_date: datetime
    is_family_safe: bool
    category: str

    @staticmethod
    def _parse_availability(raw_data: dict[str, dict]) -> PlayerAvailability:
        playability = get_by_path_or(raw_data, 'playabilityStatus')
        if playability is None:
            return PlayerAvailability(PlayerState.UNKNOWN)

        status = playability.get('status')
        try:
            state = PlayerState(status) if status else PlayerState.UNKNOWN
        except ValueError:
            # a status token that is not in the enum yet
            state = PlayerState.UNKNOWN

        reason = playability.get('reason')
        if not reason:
            messages = playability.get('messages')
            reason = messages[0] if messages else None

        return PlayerAvailability(state, reason)

    @staticmethod
    def from_json(raw_data: dict[str, dict]) -> tuple[PlayerPage | None, PlayerAvailability]:
        # The availability is decided from the playabilityStatus only, so an
        # unavailable video (no videoDetails / microformat) still reports the
        # reason of its failure instead of raising.
        availability = PlayerPage._parse_availability(raw_data)

        try:
            video_details = raw_data['videoDetails']
            microformat = get_by_path(raw_data, 'microformat playerMicroformatRenderer')
        except KeyError:
            if availability.state == PlayerState.UNKNOWN:
                raise DataParsingException('Given data is not a player page data')

            return None, availability

        try:
            return PlayerPage(
                id=video_details['videoId'],
                title=video_details['title'],
                url=microformat['canonicalUrl'],
                length_seconds=int(video_details['lengthSeconds']),
                view_count=int(video_details['viewCount']),
                thumbnails=[
                    ImageComponent.from_json(raw_thumbnail_data)
                    for raw_thumbnail_data in get_by_path(video_details, 'thumbnail thumbnails')
                ],
                description=video_details['shortDescription'],
                channel_id=video_details['channelId'],
                channel_name=microformat['ownerChannelName'],
                is_live_content=video_details['isLiveContent'],
                publish_date=datetime.fromisoformat(microformat['publishDate']),
                upload_date=datetime.fromisoformat(microformat['publishDate']),
                is_family_safe=microformat['isFamilySafe'],
                category=microformat['category']
            ), availability
        except KeyError:
            # partial videoDetails (e.g. members-only videos omit view_count)
            # — the availability verdict still carries the reason
            return None, availability
