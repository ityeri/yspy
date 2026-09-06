from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from enum import auto, Enum

from httpx import AsyncClient

from yspy.data_parsing import ImageComponent
from yspy.data_parsing.search_result import VideoComponent, ChannelComponent, SearchResultComponent
from yspy.utils import Locale, Unspecified
from .channel import Channel
from .utils import parse_subscriber_count
from .video import Video


class SearchResultType(Enum):
    VIDEO = auto()
    CHANNEL = auto()


class SearchResult(ABC):
    def __init__(self, result_type: SearchResultType, locale: Locale | None = None):
        self.result_type: SearchResultType = result_type
        # Locale value is necessary for locale persistence in methods like .get_video
        self.locale: Locale | None = locale


@dataclass
class VideoResult(SearchResult):
    id: str
    title: str
    url: str
    thumbnails: list[ImageComponent]
    is_shorts: bool
    channel_url: str
    component_data: VideoComponent
    result_type: SearchResultType = SearchResultType.VIDEO
    locale: Locale | None = None

    @staticmethod
    def from_video_component(component: VideoComponent, locale: Locale | None = None) -> VideoResult:
        return VideoResult(
            id=component.id,
            title=component.title,
            url=component.url,
            thumbnails=component.thumbnails,
            is_shorts=component.is_shorts,
            channel_url=component.channel_url,
            component_data=component,
            locale=locale
        )

    async def get_video(self, locale: Locale | None | Unspecified = Unspecified, *, client: AsyncClient | None = None):
        return await Video.aget(self.id, locale if locale != Unspecified else self.locale, client=client)

    # TODO In raw youtube video search result component, you can extract a channel id
    # Add a channel_id field at VideoComponent (SearchResultComponent)
    # and add VideoResult.aget_channel method
    # async def aget_channel(self) -> Channel: ...

    def get_highest_res_thumbnail(self) -> ImageComponent | None:
        try:
            return sorted(self.thumbnails, key=lambda t: t.width * t.height, reverse=True)[0]
        except IndexError:
            return None


@dataclass
class ChannelResult(SearchResult):
    id: str
    title: str
    url: str
    thumbnails: list[ImageComponent]
    description_snippet: str | None
    approx_subscriber_count: int | None
    component_data: ChannelComponent
    result_type: SearchResultType = SearchResultType.VIDEO
    locale: Locale | None = None

    @staticmethod
    def from_channel_component(
            component: ChannelComponent,
            locale: Locale | None = None,
            eng_component: ChannelComponent | None = None
    ) -> ChannelResult:
        # subscriber text is parsed from the English component when available —
        # the count parser only understands English abbreviated units (K/M/B)
        subscriber_count_text = (
            eng_component.subscribers_count_text
            if eng_component is not None else component.subscribers_count_text
        )
        return ChannelResult(
            id=component.id,
            title=component.title,
            url=component.url,
            thumbnails=component.thumbnails,
            description_snippet=component.description_snippet,
            approx_subscriber_count=parse_subscriber_count(subscriber_count_text),
            component_data=component,
            locale=locale
        )

    async def aget_channel(
            self, locale: Locale | None | Unspecified = Unspecified, *, client: AsyncClient | None = None
    ) -> Channel:
        return await Channel.aget(self.id, locale if locale != Unspecified else self.locale, client=client)

    def get_highest_res_thumbnail(self) -> ImageComponent | None:
        try:
            return sorted(self.thumbnails, key=lambda t: t.width * t.height, reverse=True)[0]
        except IndexError:
            return None


def from_search_result_component(
        component: SearchResultComponent,
        eng_components: dict[str, ChannelComponent] | None = None,
        locale: Locale | None = None
) -> SearchResult:
    if isinstance(component, VideoComponent):
        return VideoResult.from_video_component(component, locale)
    elif isinstance(component, ChannelComponent):
        eng_component = None
        if eng_components is not None:
            eng_component = eng_components.get(component.id)
        return ChannelResult.from_channel_component(component, locale, eng_component)
    else:
        raise TypeError('Unknown type SearchResultComponent has passed')
