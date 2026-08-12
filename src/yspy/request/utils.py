from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass, field
from typing import AsyncIterator, Any, Iterator

from httpx import AsyncClient, Response, Request, Client
from yarl import URL

from yspy.utils import Language, Region, Locale
from .constants import BASE_CLIENT_DATA, BROWSE_KEY, BASE_HEADERS


def url_with_query(endpoint: str, parameters: dict[str, Any]) -> str:
    url_obj = URL(endpoint)
    final_url = url_obj.with_query(parameters)

    return str(final_url)

def build_request_body(
        parameters: dict[str, Any],
        *,
        language: Language | None = None,
        region: Region | None = None
) -> dict[str, Any]:
    other_client_data = dict()

    if language is not None:
        other_client_data['hl'] = language
    if region is not None:
        other_client_data['gl'] = region

    return {
        'context': {
            'client': BASE_CLIENT_DATA | other_client_data,
            'user': {
                'lockedSafetyMode': False,
            }
        },
        **parameters
    }

@contextmanager
def optional_sync_client(client: Client | None = None) -> Iterator[Client]:
    is_injected = client is not None
    inner_client = client if is_injected else Client()

    try:
        yield inner_client
    finally:
        if not is_injected:
            inner_client.close()
@asynccontextmanager
async def optional_async_client(client: AsyncClient | None = None) -> AsyncIterator[AsyncClient]:
    is_injected = client is not None
    inner_client = client if is_injected else AsyncClient()

    try:
        yield inner_client
    finally:
        if not is_injected:
            await inner_client.aclose()

@dataclass
class RequestData:
    method: str
    endpoint: str
    # Yep. it's duplicated processing but more explicit
    query_params: dict[str, str] | None = field(default_factory=lambda: {'key': BROWSE_KEY})
    payload_params: dict[str, str] = field(default_factory=dict)
    no_payload: bool = False
    locale: Locale | None = None
    headers: dict[str, str] = field(default_factory=lambda: BASE_HEADERS.copy())

    def build_request(self) -> Request:
        url = str(
            URL(self.endpoint)
            .with_query(self.query_params | {'key': BROWSE_KEY})
            # Yep. it's duplicated processing but more explicit
        )

        other_client_data = dict()

        if self.locale is not None:
            if self.locale.language is not None:
                other_client_data['hl'] = self.locale.language
            if self.locale.region is not None:
                other_client_data['gl'] = self.locale.region

        if self.no_payload:
            request_payload = None
        else:
            request_payload = {
                'context': {
                    'client': BASE_CLIENT_DATA | other_client_data,
                    'user': {
                        'lockedSafetyMode': False,
                    }
                },
                **self.payload_params
            }

        return Request(
            self.method,
            url=url,
            json=request_payload,
            headers=self.headers
        )

    def send_sync_request(self, client: Client) -> Response:
        return client.send(self.build_request())
    async def send_async_request(self, client: AsyncClient) -> Response:
        return await client.send(self.build_request())
