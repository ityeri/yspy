from __future__ import annotations

from dataclasses import dataclass

from httpx import AsyncClient
from yarl import URL

from yspy.data_parsing import ImageComponent
from yspy.data_parsing.playlist import PlaylistPage, PlaylistVideoComponent
from yspy.request import PlaylistRequest
from yspy.utils import Locale, ENGLISH_LOCALE
from .exceptions import PlaylistIdentifierException
from .utils import parse_view_count, parse_length_seconds


@dataclass
class Playlist:
    id: str
    title: str
    url: str
    thumbnails: list[ImageComponent]
    owner_text: str
    owner_url: str
    view_count: int
    videos: list[PlaylistVideo]
    continuation_token: str | None
    page_index: int
    index_offset: int
    page_data: PlaylistPage

    @staticmethod
    def from_page(playlist_page: PlaylistPage, playlist_page_eng: PlaylistPage) -> Playlist:
        return Playlist(
            id=playlist_page.id,
            title=playlist_page.title,
            url=playlist_page.title,
            thumbnails=playlist_page.thumbnails,
            owner_text=playlist_page.owner_text,
            owner_url=playlist_page.owner_url,
            view_count=parse_view_count(playlist_page_eng.view_count_text),
            videos=[PlaylistVideo.from_component(video, 0) for video in playlist_page.videos],
            continuation_token=playlist_page.continuation_token,
            page_index=0,
            index_offset=0,
            page_data=playlist_page
        )

    @staticmethod
    async def aget(
            playlist_id_or_url: str,
            locale: Locale | None = None,
            client: AsyncClient | None = None
    ) -> Playlist:
        if (
                playlist_id_or_url.startswith('PL')
                or playlist_id_or_url.startswith('UU')
                or playlist_id_or_url.startswith('VL')
        ):
            playlist_id = playlist_id_or_url if playlist_id_or_url.startswith('VL') else 'VL' + playlist_id_or_url
        else:
            try:
                playlist_id = URL(playlist_id_or_url).query('list')
            except KeyError:
                raise PlaylistIdentifierException(
                    'The given playlist_id_or_url is neither a URL nor a playlist ID'
                    ' (Did you missed a PL or UU prefix or ID?)'
                )

        response = await PlaylistRequest.aget_first_page(playlist_id, locale, client=client)
        playlist_page = PlaylistPage.from_json(response.json())
        response_eng = await PlaylistRequest.aget_first_page(playlist_id, ENGLISH_LOCALE, client=client)
        playlist_page_eng = PlaylistPage.from_json(response_eng.json())

        return Playlist.from_page(playlist_page, playlist_page_eng)

    async def anext(self, locale: Locale | None = None, *, client: AsyncClient | None = None) -> Playlist | None:
        if self.continuation_token is None:
            return None

        response = await PlaylistRequest.aget_continuation_page(self.continuation_token, locale, client=client)
        next_page = PlaylistPage.from_json(response.json())
        response_eng = await PlaylistRequest.aget_continuation_page(
            self.continuation_token, ENGLISH_LOCALE, client=client
        )
        next_page_eng = PlaylistPage.from_json(response_eng.json())

        return Playlist.from_page(next_page, next_page_eng)


@dataclass
class PlaylistVideo:
    id: str
    title: str
    url: str
    thumbnails: list[ImageComponent]
    absolute_index: int
    index_offset: int
    owner_text: str
    length_seconds: int

    @staticmethod
    def from_component(component: PlaylistVideoComponent, index_offset: int) -> PlaylistVideo:
        return PlaylistVideo(
            id=component.id,
            title=component.id,
            url=component.url,
            thumbnails=component.thumbnails,
            absolute_index=index_offset + component.index,
            index_offset=index_offset,
            owner_text=component.owner_text,
            length_seconds=parse_length_seconds(component.length_text)
        )
