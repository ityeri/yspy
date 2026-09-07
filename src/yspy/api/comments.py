from __future__ import annotations

from dataclasses import dataclass

from httpx import AsyncClient, Client
from yarl import URL

from yspy.api.exceptions import VideoIdentifierException
from yspy.data_parsing import CommentComponent, VideoNextPage, CommentsPage
from yspy.request import VideoNextRequest, CommentsRequest


@dataclass
class Comments:
    comments: list[CommentComponent]
    continuation_token: str | None

    @staticmethod
    def get(video_id_or_url: str, *, client: Client | None = None) -> Comments:
        video_id = Comments._resolve_video_id(video_id_or_url)

        response = VideoNextRequest.get_page(video_id, client=client)
        video_next_page = VideoNextPage.from_json(response.json())

        response = CommentsRequest.get_page(video_next_page.comment_continuation_token, client=client)
        comments_page = CommentsPage.from_json(response.json())

        return Comments.from_comments_page(comments_page)

    @staticmethod
    async def aget(video_id_or_url: str, *, client: AsyncClient | None = None) -> Comments:
        video_id = Comments._resolve_video_id(video_id_or_url)

        response = await VideoNextRequest.aget_page(video_id, client=client)
        video_next_page = VideoNextPage.from_json(response.json())

        response = await CommentsRequest.aget_page(video_next_page.comment_continuation_token, client=client)
        comments_page = CommentsPage.from_json(response.json())

        return Comments.from_comments_page(comments_page)

    @staticmethod
    def from_comments_page(comments_page: CommentsPage) -> Comments:
        return Comments(
            comments=comments_page.comments,
            continuation_token=comments_page.continuation_token
        )

    def more(self, *, client: Client | None = None) -> Comments | None:
        if self.continuation_token is None:
            return None

        response = CommentsRequest.get_page(self.continuation_token, client=client)
        comments_page = CommentsPage.from_json(response.json())

        return Comments.from_comments_page(comments_page)

    async def amore(self, *, client: AsyncClient | None = None) -> Comments | None:
        if self.continuation_token is None:
            return None

        response = await CommentsRequest.aget_page(self.continuation_token, client=client)
        comments_page = CommentsPage.from_json(response.json())

        return Comments.from_comments_page(comments_page)

    @staticmethod
    def _resolve_video_id(video_id_or_url: str) -> str:
        if len(video_id_or_url) == 11:
            return video_id_or_url

        try:
            return URL(video_id_or_url).query['v']
        except KeyError:
            raise VideoIdentifierException('The given video_id_or_url is neither a URL nor a video ID')
