from __future__ import annotations

from dataclasses import dataclass

from yspy.utils import get_by_path, get_by_path_or

from ..image_component import ImageComponent
from ..exceptions import DataParsingException
from .search_result_component import SearchResultComponent


@dataclass
class PlaylistComponent(SearchResultComponent):
    id: str
    title: str
    url: str
    thumbnails: list[ImageComponent]
    channel_id: str | None
    channel_name: str | None

    @staticmethod
    def from_json(raw_data: dict[str, dict]) -> PlaylistComponent:
        try:
            lockup_data = raw_data['lockupViewModel']
            if lockup_data['contentType'] != 'LOCKUP_CONTENT_TYPE_PLAYLIST':
                raise DataParsingException('Given lockup data is not a playlist type data')

            metadata_rows = get_by_path(
                lockup_data,
                'metadata lockupMetadataViewModel metadata contentMetadataViewModel metadataRows'
            )

            channel_id = None
            channel_name = None
            for row in metadata_rows:
                for part in row.get('metadataParts', []):
                    command_runs = part.get('text', {}).get('commandRuns', [])
                    for command_run in command_runs:
                        browse_id = get_by_path_or(command_run, 'onTap innertubeCommand browseEndpoint browseId')
                        if browse_id is not None and browse_id.startswith('UC'):
                            channel_id = browse_id
                            channel_name = part['text']['content']
                            break
                    if channel_id is not None:
                        break
                if channel_id is not None:
                    break

            return PlaylistComponent(
                id=lockup_data['contentId'],
                title=get_by_path(lockup_data, 'metadata lockupMetadataViewModel title content'),
                url='https://youtube.com/playlist?list=' + lockup_data['contentId'],
                thumbnails=[
                    ImageComponent.from_json(raw_thumbnail_data)
                    for raw_thumbnail_data in get_by_path(
                        lockup_data,
                        'contentImage collectionThumbnailViewModel primaryThumbnail thumbnailViewModel image sources'
                    )
                ],
                channel_id=channel_id,
                channel_name=channel_name
            )
        except KeyError:
            raise DataParsingException('Given json data is not a playlist lockup data')
        except IndexError:
            raise DataParsingException('Given json data is not a playlist lockup data')
