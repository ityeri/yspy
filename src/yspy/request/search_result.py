from enum import Enum

from httpx import AsyncClient, Response, Client

from yspy.utils import Locale
from .constants import SEARCH_API_URL, BASE_HEADERS
from .utils import optional_async_client, optional_sync_client, RequestData


class SearchMode(str, Enum):
    VIDEO = 'EgIQAQ%3D%3D'
    CHANNEL = 'EgIQAg%3D%3D'
    PLAYLIST = 'EgIQAw%3D%3D' # TODO at data_parsing
    LIVESTREAM = 'EgJAAQ%3D%3D' # TODO at data_parsing

class SearchResultRequest:
    @staticmethod
    def build_first_page_request(
            query: str,
            *,
            search_mode: SearchMode | None = None,
            locale: Locale | None = None
    ) -> RequestData:
        payload_params = {'query': query}
        if search_mode:
            payload_params['params'] = search_mode
        return RequestData(
            method='POST',
            endpoint=SEARCH_API_URL,
            payload_params=payload_params,
            locale=locale,
            headers=BASE_HEADERS
        )

    @staticmethod
    def build_continuation_page_request(
            continuation_token: str,
            *,
            search_mode: SearchMode | None = None,
            locale: Locale | None = None
    ) -> RequestData:
        payload_params = {'continuation': continuation_token}
        if search_mode:
            payload_params['params'] = search_mode
        return RequestData(
            method='POST',
            endpoint=SEARCH_API_URL,
            payload_params=payload_params,
            locale=locale,
            headers=BASE_HEADERS
        )

    @staticmethod
    def get_first_page(
            query: str,
            *,
            search_mode: SearchMode | None = None,
            locale: Locale | None = None,
            client: Client | None = None
    ) -> Response:
        with optional_sync_client(client) as client:
            return SearchResultRequest.build_first_page_request(
                query, search_mode=search_mode, locale=locale
            ).send_sync_request(client)

    @staticmethod
    async def aget_first_page(
            query: str,
            *,
            search_mode: SearchMode | None = None,
            locale: Locale | None = None,
            client: AsyncClient | None = None
    ) -> Response:
        async with optional_async_client(client) as client:
            return await SearchResultRequest.build_first_page_request(
                query, search_mode=search_mode, locale=locale
            ).send_async_request(client)

    @staticmethod
    def get_continuation_page(
            continuation_token: str,
            *,
            search_mode: SearchMode | None = None,
            locale: Locale | None = None,
            client: Client | None = None
    ) -> Response:
        with optional_sync_client(client) as client:
            return SearchResultRequest.build_continuation_page_request(
                continuation_token, search_mode=search_mode, locale=locale
            ).send_sync_request(client)

    @staticmethod
    async def aget_continuation_page(
            continuation_token: str,
            *,
            search_mode: SearchMode | None = None,
            locale: Locale | None = None,
            client: AsyncClient | None = None
    ) -> Response:
        async with optional_async_client(client) as client:
            return await SearchResultRequest.build_continuation_page_request(
                continuation_token, search_mode=search_mode, locale=locale
            ).send_async_request(client)
