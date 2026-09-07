# yspy

A fork of [youtube-search-python](https://github.com/alexmercerind/youtube-search-python) rebuilt around an explicit
layer separation. Scrape YouTube search results, videos, channels, playlists and comments **without the YouTube Data
API v3**. No API key required.

- Python 3.10+
- Sync (`get_*`, `search`, `more`, `next`) and async (`aget_*`, `asearch`, `amore`, `anext`) twins everywhere
- No network calls happen at import time; every request goes through the `request` layer

## Install

```bash
pip install git+https://github.com/ityeri/yspy.git
# or from a checkout
uv sync   # dev environment (pytest included)
```

## Layer map

| Layer | Import | What it does |
|---|---|---|
| `yspy` (root) | `from yspy import Video, Channel, ...` | Re-exports the api layer for one-liner use |
| `yspy.api` | `from yspy.api import ...` | Domain objects & navigation (Video, Channel, Playlist, Search, ...) |
| `yspy.request` | `from yspy.request import ...` | HTTP layer — innertube calls, returns raw `httpx.Response` JSON |
| `yspy.data_parsing` | `from yspy.data_parsing import ...` | Pure parsing — raw JSON → frozen dataclasses, no I/O |
| `yspy.utils` | `from yspy.utils import ...` | `Locale`, `SearchMode`, path helpers |

Lower layers are public and importable, so you can build your own high-level API on top of `request` +
`data_parsing` without touching the innertube details.

---

## Quick start (root / api layer)

### Search

```python
from yspy import Search
from yspy.utils import SearchMode

# sync
search = Search.search('minecraft', SearchMode.VIDEO)
for video in search.videos:          # list[VideoResultElement]
    print(video.id, video.title)

# async
search = await Search.asearch('minecraft', SearchMode.PLAYLIST)
for playlist in search.playlists:    # list[PlaylistResultElement]
    print(playlist.title, playlist.channel_name)
```

`SearchMode` variants: `VIDEO` (default), `CHANNEL`, `PLAYLIST`, `LIVESTREAM`, or `None` for mixed results.

Continuation pages follow the same rule everywhere: **when there is no next page the call returns `None`**
instead of raising.

```python
page = Search.search('minecraft', None)
while page is not None:
    print(len(page.videos), len(page.channels))
    page = page.more()               # None on the last page
# async: await page.amore()
```

Search results expose `.videos`, `.channels`, `.playlists` plus `first_or` / `first_video_or` /
`first_channel_or`, and every element can fetch its own detail object (see below).

### Video

```python
from yspy import Video

video = Video.get('https://www.youtube.com/watch?v=6sFi_F3DJX4')   # id or URL
print(video.title, video.channel_name, video.view_count)

# async
video = await Video.aget('6sFi_F3DJX4')

# navigation
channel = await video.aget_channel()          # Video -> Channel
comments = await video.aget_comments()        # Video -> Comments
```

### Channel

```python
from yspy import Channel

channel = Channel.get('@sleepground')         # handle, URL, or UC... id
print(channel.handle_name, channel.approx_subscriber_count)

detail = await channel.aget_detail()          # Channel -> ChannelDetail
print(detail.joined_date, detail.view_count, detail.country)
```

### Playlist

```python
from yspy import Playlist

playlist = Playlist.get('PL...')              # PL/UU id, VL id or /playlist?list= URL
print(playlist.title, len(playlist.videos))

# walk all pages
page = await playlist.anext()                 # None on the last page
# uploads of a channel — 'UU' + channel_id[2:]
uploads = await Playlist.aget_from_channel(channel_id_or_url='@sleepground')
# or reuse an already fetched Channel object
uploads2 = Playlist.get_from_channel(channel=channel)

video = await playlist.videos[0].aget_video() # PlaylistVideo -> Video
```

### Comments

```python
from yspy import Comments

comments = Comments.get('6sFi_F3DJX4')
while comments is not None:
    print(len(comments.comments))
    comments = comments.more()                # None when the comment feed ends
```

### Suggestions

```python
from yspy import Suggestion

s = await Suggestion.aget('mine')
print([item.text for item in s.suggestions])
```

## Locale

YouTube renders localized count formats (`573K subscribers` vs `구독자 57.3만명`). Counts are parsed from the
**english** rendering, so a non-english locale fetches the same page twice internally — the english copy is used
only for count parsing.

```python
from yspy import Video
from yspy.utils import Locale, Language, Region, NONE_LOCALE, ENGLISH_LOCALE

ko = Locale(language=Language.KOREAN, region=Region.SOUTH_KOREA)
video = await Video.aget('6sFi_F3DJX4', ko)

# every instance method keeps the stored locale by default:
await video.aget_channel()                 # keeps ko
await video.aget_channel(NONE_LOCALE)      # explicitly no locale
await video.aget_channel(ENGLISH_LOCALE)   # override
```

`NONE_LOCALE` is the default value of every fetch argument — it sends no `hl`/`gl` and falls back to the
server/ip locale.

## Elements returned by Search

| Element | Fields (subset) | Navigation |
|---|---|---|
| `VideoResultElement` | `id, title, url, thumbnails, is_shorts, channel_id` | `get_video`/`aget_video`, `get_channel`/`aget_channel` |
| `ChannelResultElement` | `id, title, url, approx_subscriber_count` | `get_channel`/`aget_channel` |
| `PlaylistResultElement` | `id, title, url, channel_id, channel_name` | `get_playlist`/`aget_playlist`, `get_channel`/`aget_channel` |

All elements also have `get_highest_res_thumbnail()` and carry `component_data` (the underlying parsed component).

---

## Layer details

### `yspy.request` — HTTP layer

Exports: `VideoRequest`, `ChannelRequest`, `PlaylistRequest`, `SearchResultRequest`, `CommentsRequest`,
`VideoNextRequest`, `SuggestionRequest`, plus `utils` and `constants`.

Every method has a sync/async pair and returns the raw `httpx.Response`; parse it with `data_parsing`.

```python
from yspy.request import SearchResultRequest, ChannelRequest
from yspy.data_parsing.search_result import SearchResultPage
from yspy.utils import NONE_LOCALE, SearchMode

# first page and continuation
response = SearchResultRequest.get_first_page('minecraft', SearchMode.VIDEO, NONE_LOCALE)
page = SearchResultPage.from_json(response.json())
next_response = await SearchResultRequest.aget_continuation_page(page.continuation_token, SearchMode.VIDEO)

# resolve a channel handle/URL into an id (only if it is not already a UC... id)
channel_id = await ChannelRequest.aget_channel_id('https://www.youtube.com/@sleepground')
```

A plain `httpx.AsyncClient`/`Client` can be injected into any method via the keyword-only `client=` argument.

### `yspy.data_parsing` — pure parsing layer

Exports: `ImageComponent`, `VideoNextPage`, `CommentsPage`, `CommentComponent`, `SuggestionData`,
`SuggestionElement`, and the submodules

- `yspy.data_parsing.search_result`: `SearchResultPage`, `SearchResultComponent`, `VideoComponent`,
  `ChannelComponent`, `PlaylistComponent`
- `yspy.data_parsing.channel`: `ChannelPage`, `ChannelDetailPage`, `ChannelExternalLinkComponent`
- `yspy.data_parsing.playlist`: `PlaylistPage`, `PlaylistVideoComponent`
- `yspy.data_parsing.video`: `VideoPage`

Parsing is synchronous and side-effect free:

```python
from yspy.data_parsing import CommentsPage

comments_page = CommentsPage.from_json(raw_response.json())
print(comments_page.comments, comments_page.continuation_token)   # token is None when the feed ends
```

Components/pages raise `DataParsingException` (from `yspy.data_parsing.exceptions`) on malformed input.
Search/comment pages are lenient: data that is not a search page at all parses into an empty page
(`components == []`, `continuation_token is None`) instead of raising.

### `yspy.utils` — shared helpers

Exports: `Language`, `Region`, `Locale`, `NONE_LOCALE`, `ENGLISH_LOCALE`, `SearchMode`, `Unspecified`,
`get_by_path`, `get_by_path_or`, `to_youtube_url`.

- `get_by_path(data, 'a b c', 0, 'd e')` / `get_by_path_or(..., default=...)` walk nested JSON dicts/lists
  by space-separated keys — this is the same accessor used by every parser
- `NONE_LOCALE` is a module-level constant `Locale()`; `Locale` itself is a frozen dataclass of
  `language: Language | None` + `region: Region | None`

## Testing

```bash
pytest            # data_parsing unit tests against recorded fixtures (no network)
```

## Development notes

- Method order convention in api classes: fetch (sync, then async) → `from_` builders → instance pairs
  (sync above async) → private helpers
- Commit messages: `prefix: english sentence` — `add/` `edit/` `fix/` `refactor/` `format/` `rm/`
- The api layer is deliberately free of `Locale | None`; absence of a locale is spelled `NONE_LOCALE`

## Credits

Based on [youtube-search-python](https://github.com/alexmercerind/youtube-search-python) (MIT). This project is
not affiliated with YouTube.
