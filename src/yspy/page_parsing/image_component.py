from dataclasses import dataclass


@dataclass(frozen=True)
class ImageComponent:
    url: str
    width: int
    height: int
