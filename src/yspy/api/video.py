from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime
from enum import Enum

from httpx import AsyncClient, Client

from yarl import URL

from yspy.data_parsing import ImageComponent
from yspy.data_parsing.player import PlayerAvailability, PlayerPage, PlayerState
from yspy.request import PlayerRequest
from yspy.request.utils import PLAYER_FALLBACK_CLIENTS
from yspy.utils import ENGLISH_LOCALE, Locale, NONE_LOCALE
from .channel import Channel
from .comments import Comments
from .exceptions import VideoIdentifierException, VideoUnavailableException


class VideoState(str, Enum):
    # availability states of a video. the fine-grained unavailability states
    # are classified from the playability reason (the api layer may fetch with
    # an English locale, so the reason text is stable enough to compare)
    OK = 'OK'
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
    def get(
            video_id_or_url: str, locale: Locale = NONE_LOCALE, *, client: Client | None = None
    ) -> tuple[Video | None, VideoState]:
        video_id = Video._resolve_video_id(video_id_or_url)

        response = PlayerRequest.get_page(video_id, locale, client=client)
        video_page, _ = PlayerPage.from_json(response.json())
        video = Video.from_video_page(video_page, locale)
        if video is not None:
            return video, VideoState.OK

        # the page was unavailable — probe the pot-free fallback clients for a
        # truthful verdict (they answer in English by default)
        availability: PlayerAvailability | None = None
        for fallback_client in PLAYER_FALLBACK_CLIENTS:
            response = PlayerRequest.get_page(
                video_id,
                ENGLISH_LOCALE,
                client_data=fallback_client.client_data,
                headers=fallback_client.headers,
                client=client
            )
            _, availability = PlayerPage.from_json(response.json())
            if availability.state != PlayerState.UNKNOWN and availability.reason != 'The page needs to be reloaded.':
                return None, Video._get_video_state(availability)

        # every fallback client answered with a gate — keep the last verdict
        if availability is None:
            return None, VideoState.UNAVAILABLE

        return None, Video._get_video_state(availability)

    @staticmethod
    async def aget(
            video_id_or_url: str, locale: Locale = NONE_LOCALE, *, client: AsyncClient | None = None
    ) -> tuple[Video | None, VideoState]:
        video_id = Video._resolve_video_id(video_id_or_url)

        response = await PlayerRequest.aget_page(video_id, locale, client=client)
        video_page, _ = PlayerPage.from_json(response.json())
        video = Video.from_video_page(video_page, locale)
        if video is not None:
            return video, VideoState.OK

        # the page was unavailable — probe the pot-free fallback clients for a
        # truthful verdict (they answer in English by default)
        availability: PlayerAvailability | None = None
        for fallback_client in PLAYER_FALLBACK_CLIENTS:
            response = await PlayerRequest.aget_page(
                video_id,
                ENGLISH_LOCALE,
                client_data=fallback_client.client_data,
                headers=fallback_client.headers,
                client=client
            )
            _, availability = PlayerPage.from_json(response.json())
            if availability.state != PlayerState.UNKNOWN and availability.reason != 'The page needs to be reloaded.':
                return None, Video._get_video_state(availability)

        # every fallback client answered with a gate — keep the last verdict
        if availability is None:
            return None, VideoState.UNAVAILABLE

        return None, Video._get_video_state(availability)

    @staticmethod
    def from_video_page(video_page: PlayerPage | None, locale: Locale = NONE_LOCALE) -> Video | None:
        # an unavailable page produces no Video — the caller probes the
        # availability state separately
        if video_page is None:
            return None

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
    def _get_video_state(availability: PlayerAvailability) -> VideoState:
        # the message comparison follows the pytubefix case table; both
        # members-only wording variants seen in the wild are covered
        if availability.state in (PlayerState.OK, PlayerState.LIVE_STREAM, PlayerState.UNKNOWN):
            return VideoState.OK

        reason = availability.reason or ''
        state = availability.state

        if state == PlayerState.UNPLAYABLE:
            if 'members-only' in reason:
                return VideoState.MEMBERS_ONLY
            if reason == 'This live stream recording is not available.':
                return VideoState.RECORDING_UNAVAILABLE
            if 'confirm your age' in reason:
                return VideoState.AGE_RESTRICTED
            if 'copyright grounds' in reason:
                # 'blocked it in your country on copyright grounds' — copyright
                # claims are checked before plain regional blocks
                return VideoState.COPYRIGHT_BLOCKED
            if 'in your country' in reason:
                return VideoState.REGION_BLOCKED
            return VideoState.UNAVAILABLE

        if state == PlayerState.LOGIN_REQUIRED:
            if 'not a bot' in reason:
                return VideoState.BOT_DETECTION
            if 'confirm your age' in reason:
                return VideoState.AGE_RESTRICTED
            return VideoState.LOGIN_REQUIRED

        if state == PlayerState.AGE_CHECK_REQUIRED:
            return VideoState.AGE_RESTRICTED

        if state == PlayerState.ERROR:
            if 'private' in reason:
                return VideoState.PRIVATE
            if 'removed by the uploader' in reason:
                return VideoState.REMOVED_BY_UPLOADER
            if 'terminated' in reason:
                return VideoState.ACCOUNT_TERMINATED
            if 'Community Guidelines' in reason:
                return VideoState.REMOVED_FOR_TOS
            return VideoState.UNAVAILABLE

        return VideoState.UNAVAILABLE
