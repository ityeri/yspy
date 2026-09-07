from __future__ import annotations

from dataclasses import dataclass

from yspy.utils import get_by_path, get_by_path_or

from .exceptions import DataParsingException


@dataclass
class CommentComponent:
    comment: str
    author_url: str
    author_display_name: str

    @staticmethod
    def from_json(raw_data: dict) -> CommentComponent:
        try:
            return CommentComponent(
                comment=get_by_path(raw_data, 'payload commentEntityPayload properties content content'),
                author_url='https://youtube.com' + get_by_path(
                    raw_data,
                    'payload commentEntityPayload author channelCommand innertubeCommand browseEndpoint canonicalBaseUrl'
                ),
                author_display_name=get_by_path(raw_data, 'payload commentEntityPayload author displayName')
            )
        except KeyError:
            raise DataParsingException('The given data is not a comment component data')
        except IndexError:
            raise DataParsingException('The given data is not a comment component data')

@dataclass
class CommentsPage:
    comments: list[CommentComponent]
    continuation_token: str | None

    @staticmethod
    def from_json(raw_data: dict[str, dict]) -> CommentsPage:
        comment_components = list()

        raw_components = get_by_path_or(raw_data, 'frameworkUpdates entityBatchUpdate mutations')
        if raw_components is not None:
            for raw_component in raw_components:
                try:
                    comment_components.append(CommentComponent.from_json(raw_component))
                except DataParsingException:
                    pass

        token_paths = [
            [
                'onResponseReceivedEndpoints', -1, 'reloadContinuationItemsCommand',
                'continuationItems', -1, 'continuationItemRenderer',
                'continuationEndpoint continuationCommand token'
            ],
            [
                'onResponseReceivedEndpoints', -1, 'appendContinuationItemAction',
                'continuationItems', -1, 'continuationItemRenderer',
                'continuationEndpoint continuationCommand token'
            ]
        ]

        continuation_token = None
        for token_path in token_paths:
            token = get_by_path_or(raw_data, *token_path)
            if token is not None:
                continuation_token = token
                break

        return CommentsPage(
            comments=comment_components,
            continuation_token=continuation_token
        )
