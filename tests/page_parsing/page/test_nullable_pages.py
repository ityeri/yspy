import pytest

from yspy.data_parsing import CommentsPage
from yspy.data_parsing.search_result import SearchResultPage


def test_search_result_page_of_unrelated_data_is_empty():
    page = SearchResultPage.from_json({'unrelated': 1})

    assert page.components == []
    assert page.continuation_token is None


def test_search_result_page_of_empty_data_is_empty():
    page = SearchResultPage.from_json({})

    assert page.components == []
    assert page.continuation_token is None


def test_comments_page_of_unrelated_data_is_empty():
    page = CommentsPage.from_json({'unrelated': 1})

    assert page.comments == []
    assert page.continuation_token is None


def test_comments_page_of_empty_data_is_empty():
    page = CommentsPage.from_json({})

    assert page.comments == []
    assert page.continuation_token is None
