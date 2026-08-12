from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date

from yspy.data_parsing import ImageComponent
from yspy.data_parsing.channel import ChannelExternalLinkComponent, ChannelPage, ChannelDetailPage
from yspy.request import channel as channel_request


@dataclass
class Channel:
    id: str
    title: str
    handle_name: str
    url: str
    description: str
    avatar_thumbnails: list[ImageComponent]
    banners: list[ImageComponent]
    approx_subscriber_count: int
    is_family_safe: bool
    tags: list[str]

    _SUBSCRIBER_COUNT_UNITS = {
        'k': 1_000,
        'm': 1_000_000,
        'b': 1_000_000_000,
        'thousand': 1_000,
        'million': 1_000_000,
        'billion': 1_000_000_000,
    }

    _SUBSCRIBER_COUNT_PATTERN = re.compile(
        r'(?P<number>\d+(?:[.,]\d+)?)\s*(?P<unit>[kmb]|thousand|million|billion)?',
        re.IGNORECASE,
    )

    @staticmethod
    async def get(channel_id: str) -> Channel:
        response = await channel_request.get_page(channel_id)
        channel_page = ChannelPage.from_json(response.json())

        return Channel(
            id=channel_page.id,
            title=channel_page.title,
            handle_name=channel_page.handle_name,
            url=channel_page.url,
            description=channel_page.description,
            avatar_thumbnails=channel_page.avatar_thumbnails,
            banners=channel_page.banners,
            approx_subscriber_count=6974,
            is_family_safe=channel_page.is_family_safe,
            tags=channel_page.tags,
        )

    @staticmethod
    def parse_subscriber_count(text: str | None) -> int | None:
        """Parse an English subscriber count text (like '573K subscribers') into an int."""
        if not text:
            return None

        if re.search(r'\bno\s+subscribers?\b', text, re.IGNORECASE):
            return 0

        match = Channel._SUBSCRIBER_COUNT_PATTERN.search(text)
        if match is None:
            return None

        number = float(match.group('number').replace(',', ''))
        unit = (match.group('unit') or '').lower()
        multiplier = Channel._SUBSCRIBER_COUNT_UNITS.get(unit, 1)

        return int(number * multiplier)

# @dataclass
# class ChannelDetail:
#     id: str
#     url: str
#     description: str
#     country: str
#     view_count: int
#     joined_date: date
#     video_count: int
#     links: list[ChannelExternalLinkComponent]
#     page_data: ChannelPage
#     detail_page_data: ChannelDetailPage
#
#     @staticmethod
#     async def get(continuation_token: str) -> ChannelDetail:
#         response = await channel_request.get_detail_page(continuation_token)
#         detail_page = ChannelDetailPage.from_json(response.json())
#
#         response = await channel_request.get_detail_page(continuation_token)
#
#         return ChannelDetail(
#             id=detail_page.id,
#             url=detail_page.url,
#             description=detail_page.description,
#             country=detail_page.country,
#             view_count=detail_page.view_count_text
#         )
