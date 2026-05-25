from __future__ import annotations

from dataclasses import dataclass

from yspy.data_parsing import ImageComponent
from yspy.data_parsing.channel import ChannelExternalLinkComponent


@dataclass
class Channel:
    id: str
    title: str
    handle_name: str
    url: str
    description: str
    avatar_thumbnails: list[ImageComponent]
    banners: list[ImageComponent]
    subscriber_count_text: str
    video_count_text: str
    is_family_safe: bool
    tags: list[str]
    country: str
    view_count_text: str
    joined_date_text: str
    video_count_text: str
    links: list[ChannelExternalLinkComponent]


    @staticmethod
    async def get(*, channel_id: str | None = None, channel_url: str | None = None) -> Channel:
        ...