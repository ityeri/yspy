from dataclasses import dataclass


@dataclass(frozen=True)
class ImageComponent:
    url: str
    width: int
    height: int

    @staticmethod
    def from_json(raw_data: dict[str, str | int]):
        return ImageComponent(
            url=raw_data['url'],
            width=int(raw_data['width']),
            height=int(raw_data['height'])
        )
