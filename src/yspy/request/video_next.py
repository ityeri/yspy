from httpx import AsyncClient, Response

from .constants import NEXT_API_URL
from .utils import optional_async_client, RequestData


class VideoNextRequest:
    @staticmethod
    async def get_page(video_id: str, client: AsyncClient | None = None) -> Response:
        async with optional_async_client(client) as client:
            return await RequestData(
                method='POST',
                endpoint=NEXT_API_URL,
                payload_params={'videoId': video_id}
            ).send_request(client)
