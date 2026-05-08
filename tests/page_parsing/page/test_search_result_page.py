import json
from pathlib import Path

from yspy.page_parsing import SearchResultPage

with open(Path(__file__).parent / 'test_datas/search_result_page.json', 'r', encoding='utf-8') as f:
    test_first_search_result = json.load(f)

first_page = SearchResultPage.from_json(test_first_search_result, is_continuation_page=False)

breakpoint()
