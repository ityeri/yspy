from __future__ import annotations

from dataclasses import dataclass

from httpx import AsyncClient, Client
from yarl import URL

from yspy.data_parsing import ImageComponent
from yspy.data_parsing.playlist import PlaylistPage, PlaylistVideoComponent
from yspy.request import PlaylistRequest, ChannelRequest
from yspy.utils import Locale, ENGLISH_LOCALE, Unspecified, Language
from .channel import Channel
from .exceptions import PlaylistIdentifierException, ChannelIdentifierException
from .utils import parse_view_count, parse_length_seconds
from .video import Video


@dataclass
class Playlist:
    id: str
    title: str
    url: str
    thumbnails: list[ImageComponent]
    owner_text: str
    owner_url: str
    owner_id: str
    view_count: int
    videos: list[PlaylistVideo]
    continuation_token: str | None
    page_index: int
    index_offset: int
    page_data: PlaylistPage
    locale: Locale | None = None

    @staticmethod
    def get(
            playlist_id_or_url: str,
            locale: Locale | None = None,
            *,
            client: Client | None = None
    ) -> Playlist:
        playlist_id = Playlist._resolve_playlist_id(playlist_id_or_url)

        response = PlaylistRequest.get_first_page(playlist_id, locale, client=client)
        playlist_page = PlaylistPage.from_json(response.json())
        if locale is None or locale.language != Language.ENGLISH:
            # english page is required for parsing abbreviated view counts
            eng_response = PlaylistRequest.get_first_page(playlist_id, ENGLISH_LOCALE, client=client)
            eng_playlist_page = PlaylistPage.from_json(eng_response.json())
        else:
            eng_playlist_page = playlist_page

        return Playlist.from_page(playlist_page, eng_playlist_page, 0, 0, locale)

    @staticmethod
    async def aget(
            playlist_id_or_url: str,
            locale: Locale | None = None,
            *,
            client: AsyncClient | None = None
    ) -> Playlist:
        playlist_id = Playlist._resolve_playlist_id(playlist_id_or_url)

        response = await PlaylistRequest.aget_first_page(playlist_id, locale, client=client)
        playlist_page = PlaylistPage.from_json(response.json())
        if locale is None or locale.language != Language.ENGLISH:
            # english page is required for parsing abbreviated view counts
            eng_response = await PlaylistRequest.aget_first_page(playlist_id, ENGLISH_LOCALE, client=client)
            eng_playlist_page = PlaylistPage.from_json(eng_response.json())
        else:
            eng_playlist_page = playlist_page

        return Playlist.from_page(playlist_page, eng_playlist_page, 0, 0, locale)

    @staticmethod
    def from_page(
            playlist_page: PlaylistPage,
            eng_playlist_page: PlaylistPage,
            page_index: int,
            index_offset: int,
            locale: Locale | None = None
    ) -> Playlist:
        return Playlist(
            id=playlist_page.id,
            title=playlist_page.title,
            url=playlist_page.url,
            thumbnails=playlist_page.thumbnails,
            owner_text=playlist_page.owner_text,
            owner_url=playlist_page.owner_url,
            owner_id=playlist_page.owner_id,
            view_count=parse_view_count(eng_playlist_page.view_count_text),
            videos=[PlaylistVideo.from_component(video, index_offset, locale) for video in playlist_page.videos],
            continuation_token=playlist_page.continuation_token,
            page_index=page_index,
            index_offset=index_offset,
            page_data=playlist_page,
            locale=locale,
        )

    @staticmethod
    async def from_channel(
            channel: Channel | None = None,
            channel_id_or_url: str | None = None,
            locale: Locale | None = None,
            *,
            client: AsyncClient | None = None
    ) -> Playlist:
        # uploads playlist of the given channel — 'UU' + channel_id[2:]
        if channel is not None and channel_id_or_url is not None:
            raise ValueError('Only one of the parameters, channel or channel_id_or_url, should be passed')

        if channel is not None:
            channel_id = channel.id

        elif channel_id_or_url is not None:
            if channel_id_or_url.startswith('UC'):
                channel_id = channel_id_or_url
            else:
                resolved_channel_id = await ChannelRequest.aget_channel_id(channel_id_or_url, client=client)
                if resolved_channel_id is None:
                    raise ChannelIdentifierException(
                        'The given channel_id_or_url is neither a channel ID nor a channel URL'
                    )
                channel_id = resolved_channel_id

        else:
            raise ValueError('Either channel or channel_id_or_url should be passed')

        if not channel_id.startswith('UC'):
            raise ChannelIdentifierException('The given channel data is not a channel')

        return await Playlist.aget('UU' + channel_id[2:], locale, client=client)

    def get_channel(
            self, locale: Locale | None | Unspecified = Unspecified(), *, client: Client | None = None
    ) -> Channel:
        actual_locale = locale if locale != Unspecified() else self.locale
        return Channel.get(self.owner_id, actual_locale, client=client)

    async def aget_channel(
            self, locale: Locale | None | Unspecified = Unspecified(), *, client: AsyncClient | None = None
    ) -> Channel:
        actual_locale = locale if locale != Unspecified() else self.locale
        return await Channel.aget(self.owner_id, actual_locale, client=client)

    def next(
            self, locale: Locale | None | Unspecified = Unspecified(), *, client: Client | None = None
    ) -> Playlist | None:
        if self.continuation_token is None:
            return None

        actual_locale = locale if locale != Unspecified() else self.locale

        response = PlaylistRequest.get_continuation_page(self.continuation_token, actual_locale, client=client)
        next_page = PlaylistPage.from_json(response.json())
        if actual_locale is None or actual_locale.language != Language.ENGLISH:
            # english page is required for parsing abbreviated view counts
            eng_response = PlaylistRequest.get_continuation_page(
                self.continuation_token, ENGLISH_LOCALE, client=client
            )
            eng_next_page = PlaylistPage.from_json(eng_response.json())
        else:
            eng_next_page = next_page

        return Playlist.from_page(
            next_page, eng_next_page, self.page_index + 1, self.index_offset + len(self.videos), actual_locale
        )


    async def anext(
            self, locale: Locale | None | Unspecified = Unspecified(), *, client: AsyncClient | None = None
    ) -> Playlist | None:
        if self.continuation_token is None:
            return None

        actual_locale = locale if locale != Unspecified() else self.locale

        response = await PlaylistRequest.aget_continuation_page(self.continuation_token, actual_locale, client=client)
        next_page = PlaylistPage.from_json(response.json())
        if actual_locale is None or actual_locale.language != Language.ENGLISH:
            # english page is required for parsing abbreviated view counts
            eng_response = await PlaylistRequest.aget_continuation_page(
                self.continuation_token, ENGLISH_LOCALE, client=client
            )
            eng_next_page = PlaylistPage.from_json(eng_response.json())
        else:
            eng_next_page = next_page

        return Playlist.from_page(
            next_page, eng_next_page, self.page_index + 1, self.index_offset + len(self.videos), actual_locale
        )

    @staticmethod
    def _resolve_playlist_id(playlist_id_or_url: str) -> str:
        if (
                playlist_id_or_url.startswith('PL')
                or playlist_id_or_url.startswith('UU')
                or playlist_id_or_url.startswith('VL')
        ):
            return playlist_id_or_url if playlist_id_or_url.startswith('VL') else 'VL' + playlist_id_or_url

        try:
            playlist_id = URL(playlist_id_or_url).query['list']
        except KeyError:
            raise PlaylistIdentifierException(
                'The given playlist_id_or_url is neither a URL nor a playlist ID'
                ' (Did you missed a "PL" or "UU" prefix for ID?)'
            )
        return playlist_id if playlist_id.startswith('VL') else 'VL' + playlist_id

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
    locale: Locale | None = None

    @staticmethod
    def from_component(component: PlaylistVideoComponent, index_offset: int, locale: Locale | None = None) -> PlaylistVideo:
        return PlaylistVideo(
            id=component.id,
            title=component.title,
            url=component.url,
            thumbnails=component.thumbnails,
            absolute_index=index_offset + component.index,
            index_offset=index_offset,
            owner_text=component.owner_text,
            length_seconds=parse_length_seconds(component.length_text),
            locale=locale,
        )

    def get_video(
            self, locale: Locale | None | Unspecified = Unspecified(), *, client: Client | None = None
    ) -> Video:
        actual_locale = locale if locale != Unspecified() else self.locale
        return Video.get(self.id, actual_locale, client=client)

    async def aget_video(
            self, locale: Locale | None | Unspecified = Unspecified(), *, client: AsyncClient | None = None
    ) -> Video:
        actual_locale = locale if locale != Unspecified() else self.locale
        return await Video.aget(self.id, actual_locale, client=client)
