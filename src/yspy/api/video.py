from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime

from httpx import AsyncClient
from yarl import URL

from yspy.data_parsing import ImageComponent
from yspy.data_parsing.video import VideoPage
from yspy.request import VideoRequest
from yspy.utils import Locale
from .channel import Channel
from .comments import Comments


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

    @staticmethod
    async def aget(*, video_id: str | None = None, video_url: str | None = None, client: AsyncClient | None) -> Video:
        if video_id is not None and video_url is not None:
            raise ValueError('Only one of the parameters, video_id or video_url, should be passed')
        if video_url is not None:
            video_id = URL(video_url).query['v']

        response = await VideoRequest.aget_page(video_id, client=client)
        video_page = VideoPage.from_json(response.json())

        return Video.from_video_page(video_page)

    @staticmethod
    def from_video_page(video_page: VideoPage) -> Video:
        return Video(
            **{f.name: getattr(video_page, f.name) for f in fields(VideoPage)},
            page_data=video_page
        )

    async def aget_channel(self, locale: Locale | None = None, *, client: AsyncClient | None = None) -> Channel:
        return await Channel.aget(self.channel_id, locale, client=client)

    async def aget_comments(self, *, client: AsyncClient | None = None) -> Comments:
        return await Comments.aget(video_id=self.id, client=client)

    def get_highest_res_thumbnail(self) -> ImageComponent | None:
        try:
            return sorted(self.thumbnails, key=lambda t: t.width * t.height, reverse=True)[0]
        except IndexError:
            return None
