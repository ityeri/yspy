from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime
from enum import Enum

from httpx import AsyncClient, Response, Client

from yarl import URL

from yspy.data_parsing import ImageComponent
from yspy.data_parsing.player import PlayerAvailability, PlayerPage, PlayerState
from yspy.request import PlayerRequest
from yspy.request.utils import PLAYER_FALLBACK_CLIENTS
from yspy.utils import Locale, NONE_LOCALE
from .channel import Channel
from .comments import Comments
from .exceptions import VideoIdentifierException, VideoUnavailableException


class VideoUnavailableState(str, Enum):
    # fine-grained unavailability states of a video, classified from the
    # playability reason (the api layer may fetch with an English locale, so
    # the reason text is stable enough to compare against)
    MEMBERS_ONLY = 'MEMBERS_ONLY'
    RECORDING_UNAVAILABLE = 'RECORDING_UNAVAILABLE'
    AGE_RESTRICTED = 'AGE_RESTRICTED'
    BOT_DETECTION = 'BOT_DETECTION'
    LOGIN_REQUIRED = 'LOGIN_REQUIRED'
    REGION_BLOCKED = 'REGION_BLOCKED'
    COPYRIGHT_BLOCKED = 'COPYRIGHT_BLOCKED'
    PRIVATE = 'PRIVATE'
    REMOVED_BY_UPLOADER = 'REMOVED_BY_UPLOADER'
    ACCOUNT_TERMINATED = 'ACCOUNT_TERMINATED'
    REMOVED_FOR_TOS = 'REMOVED_FOR_TOS'
    UNAVAILABLE = 'UNAVAILABLE'


@dataclass
class Video:
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
    page_data: PlayerPage
    locale: Locale = NONE_LOCALE

    @staticmethod
    def get(video_id_or_url: str, locale: Locale = NONE_LOCALE, *, client: Client | None = None) -> Video:
        video_id = Video._resolve_video_id(video_id_or_url)

        video_page, availability = Video._fetch_page(video_id, locale, client)

        return Video.from_video_page(video_page, availability, locale)

    @staticmethod
    async def aget(video_id_or_url: str, locale: Locale = NONE_LOCALE, *, client: AsyncClient | None = None) -> Video:
        video_id = Video._resolve_video_id(video_id_or_url)

        video_page, availability = await Video._afetch_page(video_id, locale, client)

        return Video.from_video_page(video_page, availability, locale)

    @staticmethod
    def from_video_page(
            video_page: PlayerPage,
            availability: PlayerAvailability,
            locale: Locale = NONE_LOCALE
    ) -> Video:
        if Video._is_unavailable(availability):
            Video._raise_unavailable(availability)

        return Video(
            **{f.name: getattr(video_page, f.name) for f in fields(PlayerPage)},
            page_data=video_page,
            locale=locale
        )

    def get_channel(
            self, locale: Locale | None = None, *, client: Client | None = None
    ) -> Channel:
        actual_locale = self.locale if locale is None else locale
        return Channel.get(self.channel_id, actual_locale, client=client)

    async def aget_channel(
            self, locale: Locale | None = None, *, client: AsyncClient | None = None
    ) -> Channel:
        actual_locale = self.locale if locale is None else locale
        return await Channel.aget(self.channel_id, actual_locale, client=client)

    def get_comments(self, *, client: Client | None = None) -> Comments:
        return Comments.get(self.id, client=client)

    async def aget_comments(self, *, client: AsyncClient | None = None) -> Comments:
        return await Comments.aget(self.id, client=client)

    def get_highest_res_thumbnail(self) -> ImageComponent | None:
        try:
            return sorted(self.thumbnails, key=lambda t: t.width * t.height, reverse=True)[0]
        except IndexError:
            return None

    @staticmethod
    def _resolve_video_id(video_id_or_url: str) -> str:
        if len(video_id_or_url) == 11:
            return video_id_or_url

        try:
            return URL(video_id_or_url).query['v']
        except KeyError:
            raise VideoIdentifierException('The given video_id_or_url is neither a URL nor a video ID')

    @staticmethod
    def _fetch_page(video_id: str, locale: Locale, client: Client | None) -> tuple[PlayerPage, PlayerAvailability]:
        response = PlayerRequest.get_page(video_id, locale, client=client)
        video_page, availability = PlayerPage.from_json(response.json())

        if video_page is not None and not Video._is_unavailable(availability):
            return video_page, availability

        # the default (web) response is gated or the video is unavailable —
        # probe the pot-free fallback clients for a truthful verdict
        availability = Video._probe_availability(video_id, client)

        if Video._is_unavailable(availability):
            Video._raise_unavailable(availability)

        if video_page is None:
            # available per the probe but the default response carried no page
            response = PlayerRequest.get_page(video_id, locale, client=client)
            video_page, _ = PlayerPage.from_json(response.json())

        if video_page is None:
            raise VideoUnavailableException('The given video is not available')

        return video_page, availability

    @staticmethod
    async def _afetch_page(
            video_id: str, locale: Locale, client: AsyncClient | None
    ) -> tuple[PlayerPage, PlayerAvailability]:
        response = await PlayerRequest.aget_page(video_id, locale, client=client)
        video_page, availability = PlayerPage.from_json(response.json())

        if video_page is not None and not Video._is_unavailable(availability):
            return video_page, availability

        # the default (web) response is gated or the video is unavailable —
        # probe the pot-free fallback clients for a truthful verdict
        availability = await Video._aprobe_availability(video_id, client)

        if Video._is_unavailable(availability):
            Video._raise_unavailable(availability)

        if video_page is None:
            # available per the probe but the default response carried no page
            response = await PlayerRequest.aget_page(video_id, locale, client=client)
            video_page, _ = PlayerPage.from_json(response.json())

        if video_page is None:
            raise VideoUnavailableException('The given video is not available')

        return video_page, availability

    @staticmethod
    def _probe_availability(video_id: str, client: Client | None) -> PlayerAvailability:
        response: Response | None = None
        for fallback_client in PLAYER_FALLBACK_CLIENTS:
            response = PlayerRequest.get_page(
                video_id,
                client_data=fallback_client.client_data,
                headers=fallback_client.headers,
                client=client
            )
            _, availability = PlayerPage.from_json(response.json())
            if availability.state != PlayerState.UNKNOWN and availability.reason != 'The page needs to be reloaded.':
                return availability

        _, availability = PlayerPage.from_json(response.json())
        return availability

    @staticmethod
    async def _aprobe_availability(video_id: str, client: AsyncClient | None) -> PlayerAvailability:
        response: Response | None = None
        for fallback_client in PLAYER_FALLBACK_CLIENTS:
            response = await PlayerRequest.aget_page(
                video_id,
                client_data=fallback_client.client_data,
                headers=fallback_client.headers,
                client=client
            )
            _, availability = PlayerPage.from_json(response.json())
            if availability.state != PlayerState.UNKNOWN and availability.reason != 'The page needs to be reloaded.':
                return availability

        _, availability = PlayerPage.from_json(response.json())
        return availability

    @staticmethod
    def _is_unavailable(availability: PlayerAvailability) -> bool:
        # live streams are watchable; unknown states fall back to the page
        return availability.state not in (PlayerState.OK, PlayerState.LIVE_STREAM, PlayerState.UNKNOWN)

    @staticmethod
    def _raise_unavailable(availability: PlayerAvailability) -> None:
        fine_state = Video._classify_unavailability(availability)
        raise VideoUnavailableException(f'{availability.reason or "The given video is not available"} [{fine_state.value}]')

    @staticmethod
    def _classify_unavailability(availability: PlayerAvailability) -> VideoUnavailableState:
        # the message comparison follows the pytubefix case table; both
        # members-only wording variants seen in the wild are covered
        reason = availability.reason or ''
        state = availability.state

        if state == PlayerState.UNPLAYABLE:
            if 'members-only' in reason:
                return VideoUnavailableState.MEMBERS_ONLY
            if reason == 'This live stream recording is not available.':
                return VideoUnavailableState.RECORDING_UNAVAILABLE
            if 'confirm your age' in reason:
                return VideoUnavailableState.AGE_RESTRICTED
            if 'copyright grounds' in reason:
                # 'blocked it in your country on copyright grounds' — copyright
                # claims are checked before plain regional blocks
                return VideoUnavailableState.COPYRIGHT_BLOCKED
            if 'in your country' in reason:
                return VideoUnavailableState.REGION_BLOCKED
            return VideoUnavailableState.UNAVAILABLE

        if state == PlayerState.LOGIN_REQUIRED:
            if 'not a bot' in reason:
                return VideoUnavailableState.BOT_DETECTION
            if 'confirm your age' in reason:
                return VideoUnavailableState.AGE_RESTRICTED
            return VideoUnavailableState.LOGIN_REQUIRED

        if state == PlayerState.AGE_CHECK_REQUIRED:
            return VideoUnavailableState.AGE_RESTRICTED

        if state == PlayerState.ERROR:
            if 'private' in reason:
                return VideoUnavailableState.PRIVATE
            if 'removed by the uploader' in reason:
                return VideoUnavailableState.REMOVED_BY_UPLOADER
            if 'terminated' in reason:
                return VideoUnavailableState.ACCOUNT_TERMINATED
            if 'Community Guidelines' in reason:
                return VideoUnavailableState.REMOVED_FOR_TOS
            return VideoUnavailableState.UNAVAILABLE

        return VideoUnavailableState.UNAVAILABLE
