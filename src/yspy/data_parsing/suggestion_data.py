from __future__ import annotations

from dataclasses import dataclass
from typing import Any, TypeVar

from .exceptions import DataParsingException
from .image_component import ImageComponent
from ..utils import get_by_path_or


T = TypeVar('T')

def find_by_type(elements: list[Any], type_: type[T]) -> T:
    try:
        return next(filter(lambda x: isinstance(x, type_), elements))
    except StopIteration:
        raise ValueError('Element by given type is not found')

def find_by_type_or(elements: list[Any], type_: type[T], default = None) -> T:
    try:
        return find_by_type(elements, type_)
    except ValueError:
        return default

@dataclass
class SuggestionElement:
    text: str
    preview_image_url: ImageComponent | None
    footer: str | None
    external_url: str | None

    @staticmethod
    def from_json(raw_data: list) -> SuggestionElement:
        try:
            metadata = find_by_type_or(raw_data, dict)

            return SuggestionElement(
                text=find_by_type(raw_data, str),
                preview_image_url=get_by_path_or(metadata, 'zai'),
                footer=get_by_path_or(metadata, 'zaf'),
                external_url=get_by_path_or(metadata, 'zaq')
            )

        except ValueError:
            raise DataParsingException('The given data is not a suggestion element data')
        except KeyError:
            raise DataParsingException('The given data is not a suggestion element data')



@dataclass
class SuggestionData:
    query: str
    suggestions: list[SuggestionElement]

    @staticmethod
    def from_json(raw_data: list) -> SuggestionData:
        try:
            return SuggestionData(
                query=find_by_type(raw_data, str),
                suggestions=[
                    SuggestionElement.from_json(raw_element) for raw_element in find_by_type(raw_data, list)
                ]
            )
        except ValueError:
            raise DataParsingException('The given dat ais not a suggestions data')
