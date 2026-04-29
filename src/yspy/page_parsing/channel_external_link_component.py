from __future__ import annotations

from dataclasses import dataclass

from .image_component import ImageComponent
from ..utils import get_by_path


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
            raise ValueError('Given data is not a channel external link view model')

        return ChannelExternalLinkComponent(
            title=get_by_path(inner_data, 'title content'),
            content=get_by_path(inner_data, 'link content'),
            endpoint_url=get_by_path(inner_data, 'link commandRuns', 0, 'onTap innertubeCommand urlEndpoint url'),
            favicons=[
                ImageComponent(
                    url=raw_image_data['url'],
                    width=int(raw_image_data['width']),
                    height=int(raw_image_data['height'])
                )
                for raw_image_data in get_by_path(inner_data, 'favicon sources')
            ]
        )
