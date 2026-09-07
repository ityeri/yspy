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

BROWSE_KEY = 'AIzaSy...qcW8'

# Pot-free innertube clients that still answer the player endpoint with a
# truthful playability status anonymously (live-verified 2026-09, mirror of
# the ydpy client table). The WEB client is not included — it requires a
# po_token to reach an OK status. Each entry carries the client context
# fields and the request headers that identify that client.
PLAYER_FALLBACK_CLIENTS = (
    {
        'client_data': {
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
        'headers': {
            'User-Agent': (
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 15_7_3) AppleWebKit/605.1.15 '
                '(KHTML, like Gecko) Version/26.0 Safari/605.1.15'
            ),
            'X-YouTube-Client-Name': '101',
            'X-YouTube-Client-Version': '1.02',
        },
    },
    {
        'client_data': {
            'clientName': 'TVHTML5',
            'clientVersion': '5.20260707',
            'userAgent': 'Mozilla/5.0 (ChromiumStylePlatform) Cobalt/Version',
        },
        'headers': {
            'User-Agent': 'Mozilla/5.0 (ChromiumStylePlatform) Cobalt/Version',
            'X-YouTube-Client-Name': '7',
            'X-YouTube-Client-Version': '5.20260707',
        },
    },
    {
        'client_data': {
            'clientName': 'MWEB',
            'clientVersion': '2.20260708.05.00',
            'userAgent': (
                'Mozilla/5.0 (iPad; CPU OS 16_7_10 like Mac OS X) AppleWebKit/605.1.15 '
                '(KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1,gzip(gfe)'
            ),
        },
        'headers': {
            'User-Agent': (
                'Mozilla/5.0 (iPad; CPU OS 16_7_10 like Mac OS X) AppleWebKit/605.1.15 '
                '(KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1,gzip(gfe)'
            ),
            'X-YouTube-Client-Name': '2',
            'X-YouTube-Client-Version': '2.20260708.05.00',
        },
    },
    {
        'client_data': {
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
        'headers': {
            'User-Agent': (
                'com.google.android.apps.youtube.vr.oculus/1.65.10 '
                '(Linux; U; Android 12L; eureka-user Build/SQ3A.220605.009.A1) gzip'
            ),
            'X-YouTube-Client-Name': '28',
            'X-YouTube-Client-Version': '1.65.10',
        },
    },
)
