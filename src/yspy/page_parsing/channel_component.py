from __future__ import annotations
from dataclasses import dataclass

from yspy.utils import get_by_path


@dataclass(frozen=True)
class Thumbnail:
    url: str
    width: int
    height: int

@dataclass(frozen=True)
class ChannelComponent:
    id: str
    title: str
    url: str
    thumbnails: list[Thumbnail]
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
                Thumbnail(
                    url='https://' + raw_thumbnail_data['url'].strip('/'),
                    width=int(raw_thumbnail_data['width']),
                    height=int(raw_thumbnail_data['height'])
                ) for raw_thumbnail_data in get_by_path(inner_data, 'thumbnail thumbnails')
            ],
            description_snippet=get_by_path(inner_data, 'descriptionSnippet runs', 0, 'text'),
            subscribers_message=get_by_path(inner_data, 'videoCountText simpleText')
        )