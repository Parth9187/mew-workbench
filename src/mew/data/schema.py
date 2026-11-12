"""Immutable schemas for image-text datasets."""

from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import overload

__all__ = ["ImageTextPair", "ImageTextDataset"]


@dataclass(frozen=True, slots=True)
class ImageTextPair:
    """An image path and caption with an optional identifier."""

    image_path: Path
    caption: str
    id: str | None = None


@dataclass(frozen=True, slots=True)
class ImageTextDataset:
    """An ordered, immutable collection of image-text pairs."""

    pairs: tuple[ImageTextPair, ...]

    def __len__(self) -> int:
        return len(self.pairs)

    def __iter__(self) -> Iterator[ImageTextPair]:
        return iter(self.pairs)

    @overload
    def __getitem__(self, index: int) -> ImageTextPair: ...

    @overload
    def __getitem__(self, index: slice) -> tuple[ImageTextPair, ...]: ...

    def __getitem__(self, index: int | slice) -> ImageTextPair | tuple[ImageTextPair, ...]:
        return self.pairs[index]
