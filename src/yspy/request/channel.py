from httpx import AsyncClient, Response, Client

from yspy.utils import Locale
from .constants import BROWSE_API_URL
from .utils import optional_async_client, RequestData, optional_sync_client


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
