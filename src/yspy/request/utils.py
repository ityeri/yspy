from collections.abc import Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from functools import wraps
from typing import Optional, AsyncIterator, Any, Coroutine, TypeVar, ParamSpec
from urllib.parse import urlencode

import httpx
from httpx import AsyncClient, Response
from yarl import URL

from yspy.utils import Language, Region

BASE_CLIENT_DATA = {
    'clientName': 'WEB',
    'clientVersion': '2.20210224.06.00',
    'newVisitorCookie': True,
}

USER_AGENT = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/70.0.3538.77 Safari/537.36'
)

BASE_HEADERS = {
    'User-Agent': USER_AGENT
}

BROWSE_API_URL = 'https://www.youtube.com/youtubei/v1/browse'
SEARCH_API_URL = 'https://www.youtube.com/youtubei/v1/search'
BROWSE_KEY = 'AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8'


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

@asynccontextmanager
async def optional_async_client(client: AsyncClient | None = None) -> AsyncIterator[httpx.AsyncClient]:
    is_injected = client is not None
    inner_client = client if is_injected else httpx.AsyncClient()

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
    client_language: Language | None = None
    client_region: Region | None = None
    headers: dict[str, str] = field(default_factory=lambda: BASE_HEADERS.copy())

    async def send_request(self, client: AsyncClient) -> Response:
        other_client_data = dict()

        if self.client_language is not None:
            other_client_data['hl'] = self.client_language
        if self.client_region is not None:
            other_client_data['gl'] = self.client_region

        request_payload = {
            'context': {
                'client': BASE_CLIENT_DATA | other_client_data,
                'user': {
                    'lockedSafetyMode': False,
                }
            },
            **self.payload_params
        }

        return await client.request(
            self.method,
            url=str(URL(self.endpoint)
                    # Yep. it's duplicated processing but more explicit
                    .with_query(self.query_params | {'key': BROWSE_KEY})),
            json=request_payload,
            headers=self.headers
        )
