from httpx import Response, AsyncClient

from .constants import NEXT_API_URL
from .utils import optional_async_client, RequestData


class CommentsRequest:
    @staticmethod
    async def get_page(continuation_token: str, client: AsyncClient | None = None) -> Response:
        async with optional_async_client(client) as client:
            return await RequestData(
                method='POST',
                endpoint=NEXT_API_URL,
                payload_params={'continuation': continuation_token}
            ).send_request(client)
