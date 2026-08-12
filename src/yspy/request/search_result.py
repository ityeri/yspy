from enum import Enum

from httpx import AsyncClient, Response

from yspy.utils import Language, Region
from .constants import SEARCH_API_URL, BASE_HEADERS
from .utils import optional_async_client, RequestData


class SearchMode(str, Enum):
    VIDEO = 'EgIQAQ%3D%3D'
    CHANNEL = 'EgIQAg%3D%3D'
    PLAYLIST = 'EgIQAw%3D%3D' # TODO at data_parsing
    LIVESTREAM = 'EgJAAQ%3D%3D' # TODO at data_parsing

class SearchResultRequest:
    @staticmethod
    async def get_first_page(
            query: str,
            *,
            search_mode: SearchMode | None = None,
            language: Language | None = None,
            region: Region | None = None,
            client: AsyncClient | None = None
    ) -> Response:
        async with optional_async_client(client) as client:
            payload_params = {'query': query}
            if search_mode:
                payload_params['params'] = search_mode

            return await RequestData(
                method='POST',
                endpoint=SEARCH_API_URL,
                payload_params=payload_params,
                client_language=language,
                client_region=region,
                headers=BASE_HEADERS
            ).send_request(client)

    @staticmethod
    async def get_continuation_page(
            continuation_token: str,
            *,
            # Is these i18n-related and search_mode parameters affects to search also in continuation page request?
            # Yes it does.
            search_mode: SearchMode | None = None,
            language: Language | None = None,
            region: Region | None = None,
            client: AsyncClient | None = None
    ) -> Response:
        async with optional_async_client(client) as client:
            payload_params = {'continuation': continuation_token}
            if search_mode:
                payload_params['params'] = search_mode

            return await RequestData(
                method='POST',
                endpoint=SEARCH_API_URL,
                payload_params=payload_params,
                client_language=language,
                client_region=region,
                headers=BASE_HEADERS
            ).send_request(client)
