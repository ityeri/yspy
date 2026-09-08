from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from yspy.utils import get_by_path
from ..exceptions import DataParsingException
from ..image_component import ImageComponent


@dataclass
class PlayerPage:
    id: str
    title: str
    url: str
    length_seconds: int
    view_count: int
    thumbnails: list[ImageComponent]
    description: str
    channel_id: str
    channel_name: str
    is_live_content: bool
    publish_date: datetime
    upload_date: datetime
    is_family_safe: bool
    category: str

    @staticmethod
    def from_json(raw_data: dict[str, dict]) -> PlayerPage:
        try:
            video_details = raw_data['videoDetails']
            microformat = get_by_path(raw_data, 'microformat playerMicroformatRenderer')
        except KeyError:
            raise DataParsingException('Given data is not a video page data')

        return PlayerPage(
            id=video_details['videoId'],
            title=video_details['title'],
            url=microformat['canonicalUrl'],
            length_seconds=int(video_details['lengthSeconds']),
            view_count=int(video_details['viewCount']),
            thumbnails=[
                ImageComponent.from_json(raw_thumbnail_data)
                for raw_thumbnail_data in get_by_path(video_details, 'thumbnail thumbnails')
            ],
            description=video_details['shortDescription'],
            channel_id=video_details['channelId'],
            channel_name=microformat['ownerChannelName'],
            is_live_content=video_details['isLiveContent'],
            publish_date=datetime.fromisoformat(microformat['publishDate']),
            upload_date=datetime.fromisoformat(microformat['publishDate']),
            is_family_safe=microformat['isFamilySafe'],
            category=microformat['category']
        )
