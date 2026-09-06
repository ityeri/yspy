from __future__ import annotations

from dataclasses import dataclass

from httpx import AsyncClient, Client

from yspy.data_parsing import SuggestionElement, SuggestionData
from yspy.request import SuggestionRequest
from yspy.utils import Locale


@dataclass
class Suggestion:
    query: str
    suggestions: list[SuggestionElement]
    locale: Locale | None = None

    @staticmethod
    def get(query: str, locale: Locale | None = None, *, client: Client | None = None) -> Suggestion:
        response = SuggestionRequest.get_suggestion(query, locale, client=client)
        suggestion_data = SuggestionData.from_json(SuggestionData.unwrap_parentheses(response.text))

        return Suggestion.from_suggestion_data(suggestion_data, locale)

    @staticmethod
    async def aget(query: str, locale: Locale | None = None, *, client: AsyncClient | None = None) -> Suggestion:
        response = await SuggestionRequest.aget_suggestion(query, locale, client=client)
        suggestion_data = SuggestionData.from_json(SuggestionData.unwrap_parentheses(response.text))

        return Suggestion.from_suggestion_data(suggestion_data, locale)

    @staticmethod
    def from_suggestion_data(suggestion_data: SuggestionData, locale: Locale | None = None) -> Suggestion:
        return Suggestion(
            query=suggestion_data.query,
            suggestions=suggestion_data.suggestions,
            locale=locale,
        )
