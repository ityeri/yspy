from __future__ import annotations

import re
from dataclasses import dataclass

from yspy.utils import get_by_path

from ..exceptions import DataParsingException
from ..image_component import ImageComponent


_LENGTH_PATTERN = re.compile(r'^(?:(\d+):)?(\d+):(\d{2})$')


def _parse_length_seconds(length_text: str) -> int | None:
    match = _LENGTH_PATTERN.match(length_text)
    if match is None:
        # 'LIVE'처럼 duration이 아닌 badge 텍스트일 수 있음
        return None

    hours = int(match.group(1) or 0)
    minutes = int(match.group(2))
    seconds = int(match.group(3))

    return hours * 3600 + minutes * 60 + seconds


@dataclass
class PlaylistVideoComponent:
    id: str
    title: str
    url: str
    thumbnails: list[ImageComponent]
    index: int
    owner_text: str
    length_text: str
    length_seconds: int | None

    @staticmethod
    def from_json(raw_data: dict[str, dict], *, index: int) -> PlaylistVideoComponent:
        try:
            inner_data = raw_data['lockupViewModel']
            metadata = get_by_path(inner_data, 'metadata lockupMetadataViewModel')
            length_text = get_by_path(
                inner_data,
                'contentImage thumbnailViewModel overlays', 0,
                'thumbnailBottomOverlayViewModel badges', 0, 'thumbnailBadgeViewModel text'
            )
        except KeyError:
            raise DataParsingException('Given json data is not a playlist video lockup data')
        except IndexError:
            raise DataParsingException('Given json data is not a playlist video lockup data')

        if inner_data.get('contentType') != 'LOCKUP_CONTENT_TYPE_VIDEO':
            raise DataParsingException('Given lockup data is not a video type data')

        return PlaylistVideoComponent(
            id=inner_data['contentId'],
            title=get_by_path(metadata, 'title content'),
            url='https://youtube.com/watch?v=' + inner_data['contentId'],
            thumbnails=[
                ImageComponent.from_json(raw_thumbnail_data)
                for raw_thumbnail_data in get_by_path(inner_data, 'contentImage thumbnailViewModel image sources')
            ],
            index=index,
            owner_text=get_by_path(
                metadata,
                'metadata contentMetadataViewModel metadataRows', 0, 'metadataParts', 0, 'text content'
            ),
            length_text=length_text,
            length_seconds=_parse_length_seconds(length_text)
        )
