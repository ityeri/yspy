from enum import Enum

from httpx import AsyncClient

from .utils import optional_async_client, BASE_HEADERS, build_request_body, url_with_query, SEARCH_API_URL, BROWSE_KEY
from yspy.utils import Language, Region


class SearchMode(str, Enum):
    VIDEO = 'EgIQAQ%3D%3D'
    CHANNEL = 'EgIQAg%3D%3D'
    PLAYLIST = 'EgIQAw%3D%3D' # TODO at page_parsing
    LIVESTREAM = 'EgJAAQ%3D%3D' # TODO at page_parsing


async def get_first_page(
        query: str,
        *,
        search_mode: SearchMode | None = None,
        language: Language | None = None,
        region: Region | None = None,
        client: AsyncClient | None = None
) -> dict[str, dict]:
    other_parameters = {'query': query}
    if search_mode:
        other_parameters['params'] = search_mode

    async with optional_async_client(client) as client:
        response = await client.post(
            url=url_with_query(SEARCH_API_URL, {'key': BROWSE_KEY}),
            json=build_request_body(
                other_parameters,
                language=language,
                region=region
            ),
            headers=BASE_HEADERS
        )

        return response.json()

async def get_continuation_page( # TODO Is these parameters affects to search also in continuation page request?
        continuation_token: str,
        *,
        search_mode: SearchMode | None = None,
        language: Language | None = None,
        region: Region | None = None,
        client: AsyncClient | None = None
) -> dict[str, dict]:
    other_parameters = {'continuation': continuation_token}
    if search_mode:
        other_parameters['params'] = search_mode

    async with optional_async_client(client) as client:
        response = await client.post(
            url=url_with_query(SEARCH_API_URL, {'key': BROWSE_KEY}),
            json=build_request_body(
                other_parameters,
                language=language,
                region=region
            ),
            headers=BASE_HEADERS
        )

        return response.json()
