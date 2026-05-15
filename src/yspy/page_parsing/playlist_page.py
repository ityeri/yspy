from __future__ import annotations

from dataclasses import dataclass

from yspy.utils import get_by_path, get_by_path_or
from .image_component import ImageComponent
from .playlist_video_component import PlaylistVideoComponent


@dataclass
class PlaylistPage:
    id: str
    title: str
    url: str
    thumbnails: list[ImageComponent]
    owner_text: str
    owner_url: str
    view_count_text: str
    videos: list[PlaylistVideoComponent]
    continuation_token: str | None

    @staticmethod
    def from_json(raw_data: dict[str, dict]) -> PlaylistPage:
        try:
            sidebar_items: list[dict[str, dict]] = \
                get_by_path(raw_data, 'sidebar playlistSidebarRenderer items')
            primary_info_renderer = sidebar_items[0]['playlistSidebarPrimaryInfoRenderer']
            secondary_info_renderer = sidebar_items[1]['playlistSidebarSecondaryInfoRenderer']

            first_page_items_path = [
                'contents twoColumnBrowseResultsRenderer tabs', 0,
                'tabRenderer content sectionListRenderer contents', 0,
                'itemSectionRenderer contents', 0, 'playlistVideoListRenderer contents'
            ]
            continuation_page_items_path = [
                'onResponseReceivedActions', 0, 'appendContinuationItemsAction continuationItems'
            ]
            video_items: list[dict[str, dict]] = get_by_path_or(
                raw_data,
                *continuation_page_items_path
            )
            if video_items is None:
                video_items = get_by_path(
                    raw_data,
                    *first_page_items_path
                )

        except KeyError:
            raise ValueError('Given data is not a playlist page data')

        video_components: list[PlaylistVideoComponent] = list()

        for raw_video_data in video_items:
            try:
                video_components.append(
                    PlaylistVideoComponent.from_json(raw_video_data)
                )
            except ValueError:
                pass

        first_page_token_path = [
            'contents twoColumnBrowseResultsRenderer tabs', 0, 'tabRenderer content sectionListRenderer contents',
            0, 'itemSectionRenderer contents', 0, 'playlistVideoListRenderer contents', -1,
            'continuationItemRenderer continuationEndpoint commandExecutorCommand commands', -1,
            'continuationCommand token'
        ]
        continuation_page_token_path = [
            'onResponseReceivedActions', 0, 'appendContinuationItemsAction continuationItems',
            -1, 'continuationItemRenderer continuationEndpoint continuationCommand token'
        ]
        continuation_token = get_by_path_or(raw_data, *continuation_page_token_path)
        if continuation_token is None:
            continuation_token = get_by_path_or(raw_data, *first_page_token_path)

        return PlaylistPage(
            id=get_by_path(
                primary_info_renderer,
                'title runs', 0, 'navigationEndpoint watchEndpoint playlistId'
            ),
            title=get_by_path(primary_info_renderer, 'title runs', 0, 'text'),
            url='https://youtube.com' + get_by_path(
                primary_info_renderer,
                'title runs', 0, 'navigationEndpoint commandMetadata webCommandMetadata url'
            ),
            thumbnails=[
                ImageComponent.from_json(raw_thumbnail_data)
                for raw_thumbnail_data in get_by_path(
                    primary_info_renderer,
                    'thumbnailRenderer playlistVideoThumbnailRenderer thumbnail thumbnails'
                )
            ],
            owner_text=get_by_path(
                secondary_info_renderer,
                'videoOwner videoOwnerRenderer title runs', 0, 'text'
            ),
            owner_url='https://youtube.com' + get_by_path(
                secondary_info_renderer,
                'videoOwner videoOwnerRenderer title runs', 0,
                'navigationEndpoint browseEndpoint canonicalBaseUrl'
            ),
            view_count_text=get_by_path(primary_info_renderer, 'stats', 1, 'simpleText'),
            videos=video_components,
            continuation_token=continuation_token
        )
