from __future__ import annotations

from dataclasses import dataclass

from yspy.utils import get_by_path, get_by_path_or

from .search_result_component import SearchResultComponent
from ..exceptions import DataParsingException
from ..image_component import ImageComponent


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
    channel_id: str
    # TODO owner_text, owner_url

    @staticmethod
    def from_json(raw_data: dict[str, dict]) -> VideoComponent:
        try:
            inner_data = raw_data['videoRenderer']
        except KeyError:
            raise DataParsingException('Given json data is not a channel renderer data')

        return VideoComponent(
            id=inner_data['videoId'],
            title=get_by_path(inner_data, 'title runs', 0, 'text'),
            url='https://youtube.com'
                + get_by_path(inner_data, 'navigationEndpoint commandMetadata webCommandMetadata url'),
            thumbnails=[
                ImageComponent.from_json(raw_thumbnail_data)
                for raw_thumbnail_data in get_by_path(inner_data, 'thumbnail thumbnails')
            ],
            is_shorts='reelWatchEndpoint' in inner_data['navigationEndpoint'],
            published_time_text=get_by_path_or(inner_data, 'publishedTimeText simpleText'),
            length_text=get_by_path_or(inner_data, 'lengthText simpleText'),
            view_count_text = get_by_path_or(inner_data, 'viewCountText simpleText'),
            channel_url='https://youtube.com' + get_by_path(
                inner_data,
                'ownerText runs', 0, 'navigationEndpoint commandMetadata webCommandMetadata url'
            ),
            channel_id=get_by_path(
                inner_data,
                'ownerText runs', 0, 'navigationEndpoint browseEndpoint browseId'
            )
        )
