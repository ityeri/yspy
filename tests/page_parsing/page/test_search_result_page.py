import json
from pathlib import Path

from yspy.page_parsing.search_result import SearchResultPage

with open(Path(__file__).parent / 'test_datas/search_result_page.json', 'r', encoding='utf-8') as f:
    search_result_page = json.load(f)
with open(Path(__file__).parent / 'test_datas/search_result_continuation_page.json', 'r', encoding='utf-8') as f:
    search_result_continuation_page = json.load(f)

first_page = SearchResultPage.from_json(search_result_page)
continuation_page = SearchResultPage.from_json(search_result_continuation_page)

breakpoint()
