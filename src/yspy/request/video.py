from httpx import AsyncClient, Response

from .utils import optional_async_client, RequestData, PLAYER_API_URL


async def get_page(video_id: str, client: AsyncClient | None = None) -> Response:
    async with optional_async_client(client) as client:
        return await RequestData(
            method='POST',
            endpoint=PLAYER_API_URL,
            payload_params={
                'videoId': video_id,
                'contentCheckOk': True,
                'racyCheckOk': True
            }
        ).send_request(client)
