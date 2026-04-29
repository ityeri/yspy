from __future__ import annotations

from dataclasses import dataclass

from yspy.utils import get_by_path
from .image_component import ImageComponent
from .search_result_component import SearchResultComponent


@dataclass(frozen=True)
class ChannelComponent(SearchResultComponent):
    id: str
    title: str
    url: str
    thumbnails: list[ImageComponent]
    description_snippet: str
    subscribers_message: str

    @staticmethod
    def from_json(raw_data: dict[str, dict]) -> ChannelComponent:
        try:
            inner_data = raw_data['channelRenderer']
        except KeyError:
            raise ValueError('Given json data is not a channel renderer data')

        return ChannelComponent(
            id=inner_data['channelId'],
            title=get_by_path(inner_data, 'title simpleText'),
            url='https://youtube.com'
                + get_by_path(inner_data, 'navigationEndpoint commandMetadata webCommandMetadata url'),
            thumbnails=[
                ImageComponent.from_json(raw_thumbnail_data)
                for raw_thumbnail_data in get_by_path(inner_data, 'thumbnail thumbnails')
            ],
            description_snippet=get_by_path(inner_data, 'descriptionSnippet runs', 0, 'text'),
            subscribers_message=get_by_path(inner_data, 'videoCountText simpleText')
        )