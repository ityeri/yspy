from __future__ import annotations

from dataclasses import dataclass

from yspy.utils import get_by_path

from ..exceptions import DataParsingException
from ..image_component import ImageComponent


@dataclass
class ChannelExternalLinkComponent:
    title: str
    content: str
    endpoint_url: str
    favicons: list[ImageComponent]

    @staticmethod
    def from_json(raw_data: dict[str, dict]) -> ChannelExternalLinkComponent:
        try:
            inner_data = raw_data['channelExternalLinkViewModel']
        except KeyError:
            raise DataParsingException('Given data is not a channel external link api model')

        return ChannelExternalLinkComponent(
            title=get_by_path(inner_data, 'title content'),
            content=get_by_path(inner_data, 'link content'),
            endpoint_url=get_by_path(inner_data, 'link commandRuns', 0, 'onTap innertubeCommand urlEndpoint url'),
            favicons=[
                ImageComponent.from_json(raw_image_data)
                for raw_image_data in get_by_path(inner_data, 'favicon sources')
            ]
        )
