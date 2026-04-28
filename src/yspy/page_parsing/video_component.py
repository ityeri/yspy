from __future__ import annotations
from dataclasses import dataclass

from .search_result_component import SearchResultComponent
from .thumbnail_component import ThumbnailComponent
from yspy.utils import get_by_path


@dataclass(frozen=True)
class VideoComponent(SearchResultComponent):
    id: str
    title: str
    url: str
    thumbnails: list[ThumbnailComponent]
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

        try: published_time_text = get_by_path(inner_data, 'publishedTimeText simpleText')
        except KeyError: published_time_text = None

        try: length_text = get_by_path(inner_data, 'lengthText simpleText')
        except KeyError: length_text = None

        try: view_count_text = get_by_path(inner_data, 'viewCountText simpleText')
        except KeyError: view_count_text = None

        return VideoComponent(
            id=inner_data['videoId'],
            title=get_by_path(inner_data, 'title runs', 0, 'text'),
            url='https://youtube.com'
                + get_by_path(inner_data, 'navigationEndpoint commandMetadata webCommandMetadata url'),
            thumbnails=[
                ThumbnailComponent(
                    url='https://' + raw_thumbnail_data['url'].strip('/'),
                    width=int(raw_thumbnail_data['width']),
                    height=int(raw_thumbnail_data['height'])
                ) for raw_thumbnail_data in get_by_path(inner_data, 'thumbnail thumbnails')
            ],
            is_shorts='reelWatchEndpoint' in inner_data['navigationEndpoint'],
            published_time_text=published_time_text,
            length_text=length_text,
            view_count_text = view_count_text,
            channel_url='https://youtube.com' + get_by_path(
                inner_data,
                'ownerText runs', 0, 'navigationEndpoint commandMetadata webCommandMetadata url'
            )
        )
