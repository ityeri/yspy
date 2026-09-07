from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass, field
from typing import AsyncIterator, Iterator

from httpx import AsyncClient, Response, Request, Client
from yarl import URL

from yspy.utils import Locale

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
PLAYER_API_URL = 'https://www.youtube.com/youtubei/v1/player'
NEXT_API_URL = 'https://www.youtube.com/youtubei/v1/next'
RESOLVE_URL = 'https://www.youtube.com/youtubei/v1/navigation/resolve_url'
SUGGESTION_API_URL = 'https://clients1.google.com/complete/search'
WATCH_URL = 'https://www.youtube.com/watch'

BROWSE_KEY = 'AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8'


@dataclass(frozen=True)
class InnertubeClientData:
    # Pot-free innertube client definition for the player endpoint. The WEB
    # client is not included — it requires a po_token to reach an OK status.
    client_data: dict[str, str | bool]
    headers: dict[str, str]


# Live-verified 2026-09 (mirror of the ydpy client table): these clients still
# answer the player endpoint with a truthful playability status anonymously.
PLAYER_FALLBACK_CLIENTS: tuple[InnertubeClientData, ...] = (
    InnertubeClientData(
        client_data={
            'clientName': 'VISIONOS',
            'clientVersion': '1.02',
            'userAgent': (
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 15_7_3) AppleWebKit/605.1.15 '
                '(KHTML, like Gecko) Version/26.0 Safari/605.1.15'
            ),
            'deviceMake': 'Apple',
            'deviceModel': 'RealityDevice17,1',
            'osName': 'visionOS',
            'osVersion': '26.5.23O471',
        },
        headers={
            'User-Agent': (
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 15_7_3) AppleWebKit/605.1.15 '
                '(KHTML, like Gecko) Version/26.0 Safari/605.1.15'
            ),
            'X-YouTube-Client-Name': '101',
            'X-YouTube-Client-Version': '1.02',
        },
    ),
    InnertubeClientData(
        client_data={
            'clientName': 'TVHTML5',
            'clientVersion': '5.20260707',
            'userAgent': 'Mozilla/5.0 (ChromiumStylePlatform) Cobalt/Version',
        },
        headers={
            'User-Agent': 'Mozilla/5.0 (ChromiumStylePlatform) Cobalt/Version',
            'X-YouTube-Client-Name': '7',
            'X-YouTube-Client-Version': '5.20260707',
        },
    ),
    InnertubeClientData(
        client_data={
            'clientName': 'MWEB',
            'clientVersion': '2.20260708.05.00',
            'userAgent': (
                'Mozilla/5.0 (iPad; CPU OS 16_7_10 like Mac OS X) AppleWebKit/605.1.15 '
                '(KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1,gzip(gfe)'
            ),
        },
        headers={
            'User-Agent': (
                'Mozilla/5.0 (iPad; CPU OS 16_7_10 like Mac OS X) AppleWebKit/605.1.15 '
                '(KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1,gzip(gfe)'
            ),
            'X-YouTube-Client-Name': '2',
            'X-YouTube-Client-Version': '2.20260708.05.00',
        },
    ),
    InnertubeClientData(
        client_data={
            'clientName': 'ANDROID_VR',
            'clientVersion': '1.65.10',
            'userAgent': (
                'com.google.android.apps.youtube.vr.oculus/1.65.10 '
                '(Linux; U; Android 12L; eureka-user Build/SQ3A.220605.009.A1) gzip'
            ),
            'deviceMake': 'Oculus',
            'deviceModel': 'Quest 3',
            'osName': 'Android',
            'osVersion': '12L',
        },
        headers={
            'User-Agent': (
                'com.google.android.apps.youtube.vr.oculus/1.65.10 '
                '(Linux; U; Android 12L; eureka-user Build/SQ3A.220605.009.A1) gzip'
            ),
            'X-YouTube-Client-Name': '28',
            'X-YouTube-Client-Version': '1.65.10',
        },
    ),
)


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
    payload_params: dict[str, str | bool] = field(default_factory=dict)
    no_payload: bool = False
    locale: Locale | None = None
    headers: dict[str, str] = field(default_factory=lambda: BASE_HEADERS.copy())
    client_data: dict[str, str | bool] | None = None
    visitor_data: str | None = None

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

        client_data = dict(self.client_data) if self.client_data is not None else dict(BASE_CLIENT_DATA)
        if self.visitor_data is not None:
            client_data['visitorData'] = self.visitor_data

        if self.no_payload:
            request_payload = None
        else:
            request_payload = {
                'context': {
                    'client': client_data | other_client_data,
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
