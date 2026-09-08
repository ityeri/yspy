from httpx import AsyncClient, Response, Client

from yspy.request.utils import SUGGESTION_API_URL
from yspy.request.utils import optional_async_client, optional_sync_client, RequestData
from yspy.utils import Locale


class SuggestionRequest:
    @staticmethod
    def build_request(query: str, locale: Locale | None = None) -> RequestData:
        query_params: dict = {
            'q': query,
            'client': 'youtube',
            'gs_ri': 'youtube',
            'ds': 'yt'
        }
        if locale is not None:
            if locale.language is not None:
                query_params['hl'] = locale.language.value
            if locale.region is not None:
                query_params['gl'] = locale.region.value

        return RequestData(
            method='GET',
            endpoint=SUGGESTION_API_URL,
            query_params=query_params,
            no_payload=True
        )

    @staticmethod
    def get_suggestion(query: str, locale: Locale | None = None, *, client: Client | None = None) -> Response:
        with optional_sync_client(client) as client:
            return SuggestionRequest.build_request(query, locale).send_sync_request(client)

    @staticmethod
    async def aget_suggestion(query: str, locale: Locale | None = None, *, client: AsyncClient | None = None) -> Response:
        async with optional_async_client(client) as client:
            return await SuggestionRequest.build_request(query, locale).send_async_request(client)
