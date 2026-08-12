from httpx import AsyncClient, Response

from yspy.request.constants import SUGGESTION_API_URL
from yspy.request.utils import optional_async_client, RequestData
from yspy.utils import Language, Region


class SuggestionRequest:
    @staticmethod
    async def get_suggestion(
            query: str, language: Language, region: Region, client: AsyncClient | None = None
    ) -> Response:
        async with optional_async_client(client) as client:
            return await RequestData(
                method='GET',
                endpoint=SUGGESTION_API_URL,
                query_params={
                    'q': query,
                    'hl': language,
                    'gl': region,
                    'client': 'youtube',
                    'gs_ri': 'youtube',
                    'ds': 'yt'
                },
                no_payload=True
            ).send_request(client)
