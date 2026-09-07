import json
from pathlib import Path

import pytest

TEST_DATAS = Path(__file__).parent / 'test_datas'


def load_fixture(name):
    with open(TEST_DATAS / name, encoding='utf-8') as f:
        return json.load(f)



from yspy.data_parsing.channel import ChannelPage


def test_parse_channel_page():
    page = ChannelPage.from_json(load_fixture('channel_page.json'))

    assert page.id == 'UCDrAR1OWC2MD4s0JLetN0MA'
    assert page.title == '각별'
    assert page.handle_name == '@각별'
    assert page.url == 'https://www.youtube.com/channel/UCDrAR1OWC2MD4s0JLetN0MA'
    assert page.description == '마인크래프트 합니다.'
    assert page.subscriber_count_text == '573K subscribers'
    assert page.video_count_text == '422 videos'
    assert len(page.avatar_thumbnails) == 1
    assert len(page.banners) == 6
    assert page.is_family_safe is True
    assert len(page.tags) == 2
    assert isinstance(page.continuation_token, str) and len(page.continuation_token) > 50


def test_parse_channel_page_without_banner():
    page = ChannelPage.from_json(load_fixture('channel_page_no_banner.json'))

    assert page.id == 'UCDrAR1OWC2MD4s0JLetN0MA'
    assert page.title == '각별'
    assert page.banners == []
