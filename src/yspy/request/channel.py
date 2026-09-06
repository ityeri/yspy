from httpx import AsyncClient, Response, Client

from yspy.utils import Locale, get_by_path_or
from .constants import BROWSE_API_URL, RESOLVE_URL
from .utils import optional_async_client, RequestData, optional_sync_client


def _to_full_url(url_or_handle: str) -> str:
    if url_or_handle.startswith('http'):
        return url_or_handle
    if url_or_handle.startswith('@'):
        return 'https://www.youtube.com/' + url_or_handle
    return 'https://www.youtube.com' + url_or_handle


def _extract_channel_id(data: dict) -> str | None:
    return get_by_path_or(data, 'endpoint browseEndpoint browseId')


class ChannelRequest:
    @staticmethod
    def build_request(channel_id: str, locale: Locale | None = None) -> RequestData:
        return RequestData(
            method='POST',
            endpoint=BROWSE_API_URL,
            payload_params={'browseId': channel_id},
            locale=locale
        )
    @staticmethod
    def build_detail_page_request(continuation_token: str, locale: Locale | None = None) -> RequestData:
        return RequestData(
            method='POST',
            endpoint=BROWSE_API_URL,
            payload_params={'continuation': continuation_token},
            locale=locale
        )

    @staticmethod
    def build_resolve_request(url_or_handle: str) -> RequestData:
        # resolve_url expects a full url — bare '@handle' inputs are normalized here
        return RequestData(
            method='POST',
            endpoint=RESOLVE_URL,
            payload_params={'url': _to_full_url(url_or_handle)}
        )

    @staticmethod
    def get_channel_id(url_or_handle: str, *, client: Client | None = None) -> str | None:
        with optional_sync_client(client) as client:
            response = ChannelRequest.build_resolve_request(url_or_handle).send_sync_request(client)
            return _extract_channel_id(response.json())
    @staticmethod
    async def aget_channel_id(url_or_handle: str, *, client: AsyncClient | None = None) -> str | None:
        async with optional_async_client(client) as client:
            response = await ChannelRequest.build_resolve_request(url_or_handle).send_async_request(client)
            return _extract_channel_id(response.json())

    @staticmethod
    def get_page(channel_id: str, locale: Locale | None = None, *, client: Client | None = None) -> Response:
        with optional_sync_client(client) as client:
            return ChannelRequest.build_request(channel_id, locale).send_sync_request(client)
    @staticmethod
    async def aget_page(
            channel_id: str, locale: Locale | None = None, *, client: AsyncClient | None = None
    ) -> Response:
        async with optional_async_client(client) as client:
            return await ChannelRequest.build_request(channel_id, locale).send_async_request(client)

    @staticmethod
    def get_detail_page(
            continuation_token: str, locale: Locale | None = None, *, client: Client | None = None
    ) -> Response:
        with optional_sync_client(client) as client:
            return ChannelRequest.build_detail_page_request(continuation_token, locale).send_sync_request(client)
    @staticmethod
    async def aget_detail_page(
            continuation_token: str, locale: Locale | None = None, *, client: AsyncClient | None = None
    ) -> Response:
        async with optional_async_client(client) as client:
            return await ChannelRequest.build_detail_page_request(continuation_token, locale).send_async_request(client)
