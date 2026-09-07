from dataclasses import dataclass

from yspy.utils import get_by_path, get_by_path_or
from ..image_component import ImageComponent


@dataclass
class ChannelPage:
    id: str
    title: str
    handle_name: str
    url: str
    description: str
    avatar_thumbnails: list[ImageComponent]
    banners: list[ImageComponent]
    subscriber_count_text: str
    video_count_text: str
    is_family_safe: bool
    tags: list[str]
    continuation_token: str

    @staticmethod
    def from_json(raw_data: dict[str, dict]):
        header_data = raw_data['header']
        metadata_view_parts = get_by_path(
            header_data,
            'pageHeaderRenderer content pageHeaderViewModel metadata contentMetadataViewModel metadataRows'
        )
        channel_metadata = get_by_path(raw_data, 'metadata channelMetadataRenderer')
        microformat_data = get_by_path(raw_data, 'microformat microformatDataRenderer') # TODO, try wrap

        return ChannelPage(
            id=channel_metadata['externalId'],
            title=channel_metadata['title'],
            handle_name=get_by_path(metadata_view_parts, 0, 'metadataParts', 0, 'text content'),
            url=microformat_data['urlCanonical'],
            description=channel_metadata['description'],
            avatar_thumbnails=[
                ImageComponent.from_json(raw_thumbnail_data)
                for raw_thumbnail_data in get_by_path(channel_metadata, 'avatar thumbnails')
            ],
            banners=[
                ImageComponent.from_json(raw_image_data)
                for raw_image_data in get_by_path_or(
                    header_data,
                    'pageHeaderRenderer content pageHeaderViewModel banner imageBannerViewModel image sources',
                    default=[]
                )
            ],
            subscriber_count_text=get_by_path(metadata_view_parts, 1, 'metadataParts', 0, 'text content'),
            video_count_text=get_by_path(metadata_view_parts, 1, 'metadataParts', 1, 'text content'),
            is_family_safe=channel_metadata['isFamilySafe'],
            tags=microformat_data['tags'],
            continuation_token=get_by_path(
                header_data,
                'pageHeaderRenderer content pageHeaderViewModel description descriptionPreviewViewModel rendererContext commandContext onTap innertubeCommand showEngagementPanelEndpoint engagementPanel engagementPanelSectionListRenderer content sectionListRenderer contents', 0, 'itemSectionRenderer contents', 0, 'continuationItemRenderer continuationEndpoint continuationCommand token'
            )
        )
