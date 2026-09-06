from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from enum import auto, Enum

from httpx import AsyncClient, Client

from yspy.data_parsing import ImageComponent
from yspy.data_parsing.search_result import VideoComponent, ChannelComponent, SearchResultComponent
from yspy.utils import Locale, NONE_LOCALE
from .channel import Channel
from .utils import parse_subscriber_count
from .video import Video


class SearchResultType(Enum):
    VIDEO = auto()
    CHANNEL = auto()


@dataclass(kw_only=True)
class SearchResultElement(ABC):
    result_type: SearchResultType = SearchResultType.VIDEO
    locale: Locale = NONE_LOCALE


@dataclass
class VideoResultElement(SearchResultElement):
    id: str
    title: str
    url: str
    thumbnails: list[ImageComponent]
    is_shorts: bool
    channel_url: str
    channel_id: str
    component_data: VideoComponent

    @staticmethod
    def from_video_component(component: VideoComponent, locale: Locale = NONE_LOCALE) -> VideoResultElement:
        return VideoResultElement(
            id=component.id,
            title=component.title,
            url=component.url,
            thumbnails=component.thumbnails,
            is_shorts=component.is_shorts,
            channel_url=component.channel_url,
            channel_id=component.channel_id,
            component_data=component,
            result_type=SearchResultType.VIDEO,
            locale=locale,
        )

    def get_video(self, locale: Locale | None = None, *,
                  client: Client | None = None) -> Video:
        return Video.get(self.id, self.locale if locale is None else locale, client=client)

    async def aget_video(self, locale: Locale | None = None, *,
                         client: AsyncClient | None = None) -> Video:
        return await Video.aget(self.id, self.locale if locale is None else locale, client=client)

    def get_channel(
            self, locale: Locale | None = None, *, client: Client | None = None
    ) -> Channel:
        return Channel.get(self.channel_id, self.locale if locale is None else locale, client=client)

    async def aget_channel(
            self, locale: Locale | None = None, *, client: AsyncClient | None = None
    ) -> Channel:
        return await Channel.aget(self.channel_id, self.locale if locale is None else locale, client=client)

    def get_highest_res_thumbnail(self) -> ImageComponent | None:
        try:
            return sorted(self.thumbnails, key=lambda t: t.width * t.height, reverse=True)[0]
        except IndexError:
            return None


@dataclass
class ChannelResultElement(SearchResultElement):
    id: str
    title: str
    url: str
    thumbnails: list[ImageComponent]
    description_snippet: str | None
    approx_subscriber_count: int | None
    component_data: ChannelComponent

    @staticmethod
    def from_channel_component(
            component: ChannelComponent,
            eng_component: ChannelComponent,
            locale: Locale = NONE_LOCALE,
    ) -> ChannelResultElement:
        return ChannelResultElement(
            id=component.id,
            title=component.title,
            url=component.url,
            thumbnails=component.thumbnails,
            description_snippet=component.description_snippet,
            approx_subscriber_count=parse_subscriber_count(eng_component.subscribers_count_text),
            component_data=component,
            result_type=SearchResultType.CHANNEL,
            locale=locale,
        )

    def get_channel(
            self, locale: Locale | None = None, *, client: Client | None = None
    ) -> Channel:
        return Channel.get(self.id, self.locale if locale is None else locale, client=client)

    async def aget_channel(
            self, locale: Locale | None = None, *, client: AsyncClient | None = None
    ) -> Channel:
        return await Channel.aget(self.id, self.locale if locale is None else locale, client=client)

    def get_highest_res_thumbnail(self) -> ImageComponent | None:
        try:
            return sorted(self.thumbnails, key=lambda t: t.width * t.height, reverse=True)[0]
        except IndexError:
            return None


def from_search_result_component(
        component: SearchResultComponent,
        eng_component: SearchResultComponent,
        locale: Locale = NONE_LOCALE
) -> SearchResultElement:
    if isinstance(component, VideoComponent):
        return VideoResultElement.from_video_component(component, locale)
    elif isinstance(component, ChannelComponent):
        return ChannelResultElement.from_channel_component(component, eng_component, locale)
    else:
        raise TypeError('Unknown type SearchResultComponent has passed')
