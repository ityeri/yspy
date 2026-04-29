from __future__ import annotations
from dataclasses import dataclass

from .search_result_component import SearchResultComponent
from .image_component import ImageComponent
from yspy.utils import get_by_path, get_by_path_or


@dataclass(frozen=True)
class VideoComponent(SearchResultComponent):
    id: str
    title: str
    url: str
    thumbnails: list[ImageComponent]
    is_shorts: bool
    published_time_text: str | None
    length_text: str
    view_count_text: str
    channel_url: str

    @staticmethod
    def from_json(raw_data: dict[str, dict]) -> VideoComponent:
        try:
            inner_data = raw_data['videoRenderer']
        except KeyError:
            raise ValueError('Given json data is not a channel renderer data')

        return VideoComponent(
            id=inner_data['videoId'],
            title=get_by_path(inner_data, 'title runs', 0, 'text'),
            url='https://youtube.com'
                + get_by_path(inner_data, 'navigationEndpoint commandMetadata webCommandMetadata url'),
            thumbnails=[
                ImageComponent(
                    url='https://' + raw_thumbnail_data['url'].strip('/'),
                    width=int(raw_thumbnail_data['width']),
                    height=int(raw_thumbnail_data['height'])
                ) for raw_thumbnail_data in get_by_path(inner_data, 'thumbnail thumbnails')
            ],
            is_shorts='reelWatchEndpoint' in inner_data['navigationEndpoint'],
            published_time_text=get_by_path_or(inner_data, 'publishedTimeText simpleText'),
            length_text=get_by_path_or(inner_data, 'lengthText simpleText'),
            view_count_text = get_by_path_or(inner_data, 'viewCountText simpleText'),
            channel_url='https://youtube.com' + get_by_path(
                inner_data,
                'ownerText runs', 0, 'navigationEndpoint commandMetadata webCommandMetadata url'
            )
        )
