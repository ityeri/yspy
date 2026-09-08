from httpx import Response, AsyncClient, Client

from .utils import NEXT_API_URL
from .utils import optional_async_client, optional_sync_client, RequestData


class CommentsRequest:
    @staticmethod
    def build_request(continuation_token: str) -> RequestData:
        return RequestData(
            method='POST',
            endpoint=NEXT_API_URL,
            payload_params={'continuation': continuation_token}
        )

    @staticmethod
    def get_page(continuation_token: str, *, client: Client | None = None) -> Response:
        with optional_sync_client(client) as client:
            return CommentsRequest.build_request(continuation_token).send_sync_request(client)

    @staticmethod
    async def aget_page(continuation_token: str, *, client: AsyncClient | None = None) -> Response:
        async with optional_async_client(client) as client:
            return await CommentsRequest.build_request(continuation_token).send_async_request(client)
