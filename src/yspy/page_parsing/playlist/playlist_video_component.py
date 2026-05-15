from __future__ import annotations

from dataclasses import dataclass

from ..image_component import ImageComponent
from yspy.utils import get_by_path


@dataclass
class PlaylistVideoComponent:
    id: str
    title: str
    url: str
    thumbnails: list[ImageComponent]
    index: int
    owner_text: str
    owner_url: str
    length_text: str
    length_seconds: int
    is_playable: bool

    @staticmethod
    def from_json(raw_data: dict[str, dict]) -> PlaylistVideoComponent:
        try:
            inner_data = raw_data['playlistVideoRenderer']
        except KeyError:
            raise ValueError('Given data is not a playlist video renderer data')

        return PlaylistVideoComponent(
            id=inner_data['videoId'],
            title=get_by_path(inner_data, 'title runs', 0, 'text'),
            url='https://youtube.com'
                + get_by_path(inner_data, 'navigationEndpoint commandMetadata webCommandMetadata url'),
            thumbnails=[
                ImageComponent.from_json(
                    raw_thumbnail_data
                )
                for raw_thumbnail_data in get_by_path(inner_data, 'thumbnail thumbnails')
            ],
            index=int(get_by_path(inner_data, 'index simpleText')),
            owner_text=get_by_path(inner_data, 'shortBylineText runs', 0, 'text'),
            owner_url='https://youtube.com' + get_by_path(
                inner_data,
                'shortBylineText runs', 0, 'navigationEndpoint commandMetadata webCommandMetadata url'
            ),
            length_text=get_by_path(inner_data, 'lengthText simpleText'),
            length_seconds=int(get_by_path(inner_data, 'lengthSeconds')),
            is_playable=inner_data['isPlayable']
        )
