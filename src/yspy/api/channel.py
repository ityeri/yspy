from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from httpx import AsyncClient, Client

from yspy.data_parsing import ImageComponent
from yspy.data_parsing.channel import ChannelPage, ChannelExternalLinkComponent, ChannelDetailPage
from yspy.request import ChannelRequest
from yspy.utils import Locale, ENGLISH_LOCALE, Unspecified, Language
from .exceptions import ChannelIdentifierException
from .utils import parse_subscriber_count, parse_view_count, parse_joined_date, parse_video_count


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
    page_data: ChannelPage
    continuation_token: str
    locale: Locale | None = None

    @staticmethod
    def from_channel_page(
            channel_page: ChannelPage,
            eng_channel_page: ChannelPage,
            locale: Locale | None = None
    ) -> Channel:
        return Channel(
            id=channel_page.id,
            title=channel_page.title,
            handle_name=channel_page.handle_name,
            url=channel_page.url,
            description=channel_page.description,
            avatar_thumbnails=channel_page.avatar_thumbnails,
            banners=channel_page.banners,
            approx_subscriber_count=parse_subscriber_count(eng_channel_page.subscriber_count_text),
            is_family_safe=channel_page.is_family_safe,
            tags=channel_page.tags,
            page_data=channel_page,
            continuation_token=channel_page.continuation_token,
            locale=locale,
        )

    @staticmethod
    async def aget(
            channel_id_or_url: str, locale: Locale | None = None, *, client: AsyncClient | None = None
    ) -> Channel:
        if channel_id_or_url.startswith('UC'):
            channel_id = channel_id_or_url
        else:
            channel_id = await ChannelRequest.aget_channel_id(channel_id_or_url, client=client)
            if channel_id is None:
                raise ChannelIdentifierException(
                    'The given channel_id_or_url is neither a channel ID nor a channel URL'
                )

        response = await ChannelRequest.aget_page(channel_id, locale, client=client)
        channel_page = ChannelPage.from_json(response.json())
        if locale is None or locale.language != Language.ENGLISH:
            # english page is required for parsing abbreviated counts (K/M/B)
            response = await ChannelRequest.aget_page(channel_id, ENGLISH_LOCALE, client=client)
            eng_channel_page = ChannelPage.from_json(response.json())
        else:
            eng_channel_page = channel_page

        return Channel.from_channel_page(channel_page, eng_channel_page, locale)

    @staticmethod
    def get(
            channel_id_or_url: str, locale: Locale | None = None, *, client: Client | None = None
    ) -> Channel:
        if channel_id_or_url.startswith('UC'):
            channel_id = channel_id_or_url
        else:
            channel_id = ChannelRequest.get_channel_id(channel_id_or_url, client=client)
            if channel_id is None:
                raise ChannelIdentifierException(
                    'The given channel_id_or_url is neither a channel ID nor a channel URL'
                )

        response = ChannelRequest.get_page(channel_id, locale, client=client)
        channel_page = ChannelPage.from_json(response.json())
        if locale is None or locale.language != Language.ENGLISH:
            # english page is required for parsing abbreviated counts (K/M/B)
            response = ChannelRequest.get_page(channel_id, ENGLISH_LOCALE, client=client)
            eng_channel_page = ChannelPage.from_json(response.json())
        else:
            eng_channel_page = channel_page

        return Channel.from_channel_page(channel_page, eng_channel_page, locale)

    async def aget_detail(
            self, locale: Locale | None | Unspecified = Unspecified(), *, client: AsyncClient | None = None
    ) -> ChannelDetail:
        actual_locale = locale if locale != Unspecified() else self.locale
        return await ChannelDetail.aget(self.continuation_token, actual_locale, client=client)

    def get_detail(
            self, locale: Locale | None | Unspecified = Unspecified(), *, client: Client | None = None
    ) -> ChannelDetail:
        actual_locale = locale if locale != Unspecified() else self.locale
        return ChannelDetail.get(self.continuation_token, actual_locale, client=client)


@dataclass
class ChannelDetail:
    id: str
    url: str
    description: str
    country: str
    approx_subscriber_count: int
    view_count: int
    joined_date: date
    video_count: int
    links: list[ChannelExternalLinkComponent]
    page_data: ChannelDetailPage
    locale: Locale | None = None

    @staticmethod
    def from_detail_page(
            detail_page: ChannelDetailPage,
            eng_detail_page: ChannelDetailPage,
            locale: Locale | None = None
    ) -> ChannelDetail:
        return ChannelDetail(
            id=detail_page.id,
            url=detail_page.url,
            description=detail_page.description,
            country=detail_page.country,
            approx_subscriber_count=parse_subscriber_count(eng_detail_page.subscriber_count_text),
            view_count=parse_view_count(eng_detail_page.view_count_text),
            joined_date=parse_joined_date(eng_detail_page.joined_date_text),
            video_count=parse_video_count(eng_detail_page.video_count_text),
            links=detail_page.links,
            page_data=detail_page,
            locale=locale,
        )

    @staticmethod
    async def aget(
            continuation_token: str, locale: Locale | None = None, *, client: AsyncClient | None = None
    ) -> ChannelDetail:
        response = await ChannelRequest.aget_detail_page(continuation_token, locale, client=client)
        detail_page = ChannelDetailPage.from_json(response.json())
        if locale is None or locale.language != Language.ENGLISH:
            # english page is required for parsing abbreviated counts and joined date
            response = await ChannelRequest.aget_detail_page(continuation_token, ENGLISH_LOCALE, client=client)
            eng_detail_page = ChannelDetailPage.from_json(response.json())
        else:
            eng_detail_page = detail_page

        return ChannelDetail.from_detail_page(detail_page, eng_detail_page, locale)

    @staticmethod
    def get(
            continuation_token: str, locale: Locale | None = None, *, client: Client | None = None
    ) -> ChannelDetail:
        response = ChannelRequest.get_detail_page(continuation_token, locale, client=client)
        detail_page = ChannelDetailPage.from_json(response.json())
        if locale is None or locale.language != Language.ENGLISH:
            # english page is required for parsing abbreviated counts and joined date
            response = ChannelRequest.get_detail_page(continuation_token, ENGLISH_LOCALE, client=client)
            eng_detail_page = ChannelDetailPage.from_json(response.json())
        else:
            eng_detail_page = detail_page

        return ChannelDetail.from_detail_page(detail_page, eng_detail_page, locale)
