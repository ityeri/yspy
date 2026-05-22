from dataclasses import dataclass

from yspy.utils import get_by_path

from .channel_external_link_component import ChannelExternalLinkComponent
from ..exceptions import PageParsingException


@dataclass
class ChannelDetailPage:
    id: str
    url: str
    description: str
    country: str
    subscriber_count_text: str
    view_count_text: str
    joined_date_text: str
    video_count_text: str
    links: list[ChannelExternalLinkComponent]

    @staticmethod
    def from_json(raw_data: dict[str, dict]):
        try:
            inner_data = get_by_path(
                raw_data,
                'onResponseReceivedEndpoints', 0,
                'appendContinuationItemsAction continuationItems', 0, 'aboutChannelRenderer'
            )
        except KeyError:
            raise PageParsingException('Given data is not a channel detail page(popup ui) data')

        about_channel_view_data = get_by_path(inner_data, 'metadata aboutChannelViewModel')

        return ChannelDetailPage(
            id=about_channel_view_data['channelId'],
            url=about_channel_view_data['canonicalChannelUrl'],
            description=about_channel_view_data['description'],
            country=about_channel_view_data['country'],
            subscriber_count_text=about_channel_view_data['subscriberCountText'],
            view_count_text=about_channel_view_data['viewCountText'],
            joined_date_text=get_by_path(about_channel_view_data, 'joinedDateText content'),
            video_count_text=get_by_path(about_channel_view_data['videoCountText']),
            links=[
                ChannelExternalLinkComponent.from_json(raw_link_data)
                for raw_link_data in about_channel_view_data['links']
            ]
        )
