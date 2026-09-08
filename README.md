<h1 align="center">yspy</h1>

<div align="center">
  <b><code>Youtube.</code></b><br>
  <b><code>Search..</code></b><br>
  <b><code>PYthon..</code></b><br>
</div>

<br>

<p align="center">
  Scrape YouTube search results, videos, channels, playlists and comments
  <strong>without the YouTube Data API v3</strong>. No API key required.
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
  <img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python: 3.10+">
  <img src="https://img.shields.io/pypi/v/yspy" alt="PyPI version">
</p>

---

A refactored fork of [youtube-search-python](https://github.com/alexmercerind/youtube-search-python)
rebuilt around a clean-room code.

- python >= 3.10
- Sync (`get_*`, `search`, `more`, `next`) and async (`aget_*`, `asearch`, `amore`, `anext`) twins everywhere
    - Async is not just a wrapper for a sync API. Both have separate request paths.
- Minimized unexpected network calls, behaviors
- `Video.get` / `Video.aget` return a `(Video | None, VideoState)` availability verdict — no exceptions

## Install

Using uv & pip

```bash
pip install yspy # or: uv add yspy
```

Using pyproject.toml

```toml
[project]
dependencies = [
    "yspy"
]
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

`SearchMode` variants: `VIDEO` (default), `CHANNEL`, `PLAYLIST`, `LIVESTREAM`, or `None`(default) for mixed results.

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
from yspy import Video, VideoState

video, state = Video.get('https://www.youtube.com/watch?v=6sFi_F3DJX4')  # id or URL
if state is VideoState.OK:
    print(video.title, video.channel_name, video.view_count)

# async
video, state = await Video.aget('6sFi_F3DJX4')
```

`Video.get` / `Video.aget` return `(Video | None, VideoState)` instead of raising.
`VideoState.OK` means the video is available; otherwise `video` is `None` and the state tells why:
`MEMBERS_ONLY`, `RECORDING_UNAVAILABLE`, `AGE_RESTRICTED`, `BOT_DETECTION`, `LOGIN_REQUIRED`,
`REGION_BLOCKED`, `COPYRIGHT_BLOCKED`, `PRIVATE`, `REMOVED_BY_UPLOADER`, `ACCOUNT_TERMINATED`,
`REMOVED_FOR_TOS`, `UNAVAILABLE`. The verdict is classified from the playability reason, so when a
page comes back unavailable the library re-probes once with pot-free innertube clients (in English).

```python
video, state = await Video.aget('https://www.youtube.com/watch?v=C0Rs8MDpHsM')  # members-only
print(state)  # VideoState.MEMBERS_ONLY, video is None
```

```python
# navigation (on a fetched Video — i.e. when state is OK)
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
