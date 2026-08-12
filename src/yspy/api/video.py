from __future__ import annotations

from dataclasses import dataclass, fields

from yarl import URL

from yspy.data_parsing.video import VideoPage
from yspy.request import video as video_request
from .channel import Channel


@dataclass
class Video(VideoPage):
    page_data: VideoPage

    async def get_channel(self) -> Channel:
        ...

    @staticmethod
    def from_video_page(video_page: VideoPage) -> Video:
        return Video(
            **{f.name: getattr(video_page, f.name) for f in fields(VideoPage)},
            page_data=video_page
        )

    @staticmethod
    async def get(*, video_id: str | None = None, video_url: str | None = None) -> Video:
        if video_id is not None and video_url is not None:
            raise ValueError('Only one of the parameters, video_id or video_url, should be passed')

        if video_url is not None:
            video_id = URL(video_url).query['v']

        response = await video_request.get_page(video_id)
        video_page = VideoPage.from_json(response.json())

        return Video.from_video_page(video_page)
