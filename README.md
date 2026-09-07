# yspy

A refactored fork of [youtube-search-python](https://github.com/alexmercerind/youtube-search-python)
rebuilt around a clean-room code.
Scrape YouTube search results, videos, channels, playlists and comments
**without the YouTube Data API v3**. No API key required.

- Python 3.10+
- Sync (`get_*`, `search`, `more`, `next`) and async (`aget_*`, `asearch`, `amore`, `anext`) twins everywhere
    - Async is not just a wrapper for a sync API. Both have separate request paths.
- Minimized unexpected network calls, behaviors

## Install

```bash
pip install git+https://github.com/ityeri/yspy.git
# or from a checkout
uv sync   # dev environment (pytest included)
```

## Quick start (root / api layer)

### Search

```python
from yspy import Search
from yspy.utils import SearchMode

# sync
search = Search.search('minecraft', SearchMode.VIDEO)
for video in search.videos:  # list[VideoResultElement]
    print(video.id, video.title)

# async
search = await Search.asearch('minecraft', SearchMode.PLAYLIST)
for playlist in search.playlists:  # list[PlaylistResultElement]
    print(playlist.title, playlist.channel_name)
```

`SearchMode` variants: `VIDEO` (default), `CHANNEL`, `PLAYLIST`, `LIVESTREAM`, or `None` for mixed results.

Continuation pages follow the same rule everywhere: **when there is no next page the call returns `None`**
instead of raising.

```python
page = Search.search('minecraft', None)
while page is not None:
    print(len(page.videos), len(page.channels))
    page = page.more()  # None on the last page
# async: await page.amore()
```

Search results expose `.videos`, `.channels`, `.playlists` plus `first_or` / `first_video_or` /
`first_channel_or`, and every element can fetch its own detail object (see below).

### Video

```python
from yspy import Video

video = Video.get('https://www.youtube.com/watch?v=6sFi_F3DJX4')  # id or URL
print(video.title, video.channel_name, video.view_count)

# async
video = await Video.aget('6sFi_F3DJX4')

# navigation
channel = await video.aget_channel()  # Video -> Channel
comments = await video.aget_comments()  # Video -> Comments
```

### Channel

```python
from yspy import Channel

channel = Channel.get('@sleepground')  # handle, URL, or UC... id
print(channel.handle_name, channel.approx_subscriber_count)

detail = await channel.aget_detail()  # Channel -> ChannelDetail
print(detail.joined_date, detail.view_count, detail.country)
```

### Playlist

```python
from yspy import Playlist

playlist = Playlist.get('PL...')  # PL/UU id, VL id or /playlist?list= URL
print(playlist.title, len(playlist.videos))

# walk all pages
page = await playlist.anext()  # None on the last page
# uploads of a channel — 'UU' + channel_id[2:]
uploads = await Playlist.aget_from_channel(channel_id_or_url='@sleepground')
# or reuse an already fetched Channel object
uploads2 = Playlist.get_from_channel(channel=channel)

video = await playlist.videos[0].aget_video()  # PlaylistVideo -> Video
```

### Comments

```python
from yspy import Comments

comments = Comments.get('6sFi_F3DJX4')
while comments is not None:
    print(len(comments.comments))
    comments = comments.more()  # None when the comment feed ends
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
await video.aget_channel()  # keeps ko
await video.aget_channel(NONE_LOCALE)  # explicitly no locale
await video.aget_channel(ENGLISH_LOCALE)  # override
```

`NONE_LOCALE` is the default value of every fetch argument — it sends no `hl`/`gl`
and in this case, the YouTube api usually falls back to the server/IP locale.

## Elements returned by Search

| Element                 | Navigation                                                   |
|-------------------------|--------------------------------------------------------------|
| `VideoResultElement`    | `get_video`/`aget_video`, `get_channel`/`aget_channel`       |
| `ChannelResultElement`  | `get_channel`/`aget_channel`                                 |
| `PlaylistResultElement` | `get_playlist`/`aget_playlist`, `get_channel`/`aget_channel` |

All elements also have `get_highest_res_thumbnail()` and carry `component_data` (the underlying parsed component).

## Layer map

`ysps` is separated in a few of layers followed by their functions and responsibilities:

| Layer               | What it does                                                        |
|---------------------|---------------------------------------------------------------------|
| `yspy.api`          | Domain objects & navigation (Video, Channel, Playlist, Search, ...) |
| `yspy.request`      | HTTP layer — innertube calls, returns raw `httpx.Response` JSON     |
| `yspy.data_parsing` | Pure parsing — raw JSON → frozen dataclasses, no I/O                |
| `yspy.utils`        | `Locale`, `SearchMode`, path helpers                                |

Lower layers are public and importable,
so you can access to `request` + `data_parsing` layer directly without touching innertube requests.

## Credits

Based on [youtube-search-python](https://github.com/alexmercerind/youtube-search-python) (MIT).
This project is not affiliated with YouTube.
