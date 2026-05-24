from httpx import AsyncClient, Response

from yspy.request.utils import optional_async_client, RequestData, SUGGESTION_API_URL
from yspy.utils import Language, Region


async def get_suggestion(query: str, language: Language, region: Region, client: AsyncClient | None = None) -> Response:
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
