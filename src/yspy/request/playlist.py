from httpx import AsyncClient, Response, Client

from yspy.utils import Locale
from .constants import BROWSE_API_URL, BASE_HEADERS
from .utils import optional_async_client, optional_sync_client, RequestData


class PlaylistRequest:
    @staticmethod
    def build_first_page_request(browse_id: str, locale: Locale | None = None) -> RequestData:
        # A playlist page browse id is 'VL' + playlist_id — callers build it beforehand
        return RequestData(
            method='POST',
            endpoint=BROWSE_API_URL,
            payload_params={'browseId': browse_id},
            locale=locale,
            headers=BASE_HEADERS
        )

    @staticmethod
    def build_continuation_page_request(continuation_token: str, locale: Locale | None = None) -> RequestData:
        return RequestData(
            method='POST',
            endpoint=BROWSE_API_URL,
            payload_params={'continuation': continuation_token},
            locale=locale,
            headers=BASE_HEADERS
        )

    @staticmethod
    def get_first_page(browse_id: str, locale: Locale | None = None, *, client: Client | None = None) -> Response:
        with optional_sync_client(client) as client:
            return PlaylistRequest.build_first_page_request(browse_id, locale).send_sync_request(client)

    @staticmethod
    async def aget_first_page(
            browse_id: str, locale: Locale | None = None, *, client: AsyncClient | None = None
    ) -> Response:
        async with optional_async_client(client) as client:
            return await PlaylistRequest.build_first_page_request(browse_id, locale).send_async_request(client)

    @staticmethod
    def get_continuation_page(
            continuation_token: str, locale: Locale | None = None, *, client: Client | None = None
    ) -> Response:
        with optional_sync_client(client) as client:
            return PlaylistRequest.build_continuation_page_request(continuation_token, locale).send_sync_request(client)

    @staticmethod
    async def aget_continuation_page(
            continuation_token: str, locale: Locale | None = None, *, client: AsyncClient | None = None
    ) -> Response:
        async with optional_async_client(client) as client:
            return await PlaylistRequest.build_continuation_page_request(continuation_token, locale)\
                .send_async_request(client)
