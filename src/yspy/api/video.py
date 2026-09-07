from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime

from httpx import AsyncClient, Client
from yarl import URL

from yspy.data_parsing import ImageComponent
from yspy.data_parsing.video import VideoPage
from yspy.request import PlayerRequest
from yspy.utils import Locale, NONE_LOCALE
from .channel import Channel
from .comments import Comments
from .exceptions import VideoIdentifierException


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
    page_data: VideoPage
    locale: Locale = NONE_LOCALE

    @staticmethod
    def get(video_id_or_url: str, locale: Locale = NONE_LOCALE, *, client: Client | None = None) -> Video:
        video_id = Video._resolve_video_id(video_id_or_url)

        response = PlayerRequest.get_page(video_id, locale, client=client)
        video_page = VideoPage.from_json(response.json())

        return Video.from_video_page(video_page, locale)

    @staticmethod
    async def aget(video_id_or_url: str, locale: Locale = NONE_LOCALE, *, client: AsyncClient | None = None) -> Video:
        video_id = Video._resolve_video_id(video_id_or_url)

        response = await PlayerRequest.aget_page(video_id, locale, client=client)
        video_page = VideoPage.from_json(response.json())

        return Video.from_video_page(video_page, locale)

    @staticmethod
    def from_video_page(video_page: VideoPage, locale: Locale = NONE_LOCALE) -> Video:
        return Video(
            **{f.name: getattr(video_page, f.name) for f in fields(VideoPage)},
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
