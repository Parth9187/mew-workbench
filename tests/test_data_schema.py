"""Tests for the public image-text dataset schemas."""

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from mew.data import ImageTextDataset, ImageTextPair


def test_pair_construction() -> None:
    path = Path("images/../cat.jpg")
    pair = ImageTextPair(path, "A cat")

    assert pair.image_path is path
    assert pair.caption == "A cat"
    assert pair.id is None


def test_pair_optional_id() -> None:
    pair = ImageTextPair(Path("cat.jpg"), "A cat", "cat-1")

    assert pair.id == "cat-1"


def test_empty_dataset() -> None:
    dataset = ImageTextDataset(())

    assert dataset.pairs == ()
    assert len(dataset) == 0
    assert tuple(dataset) == ()
    assert dataset[:] == ()
    with pytest.raises(IndexError):
        dataset[0]


@pytest.fixture
def pairs() -> tuple[ImageTextPair, ...]:
    return tuple(ImageTextPair(Path(f"{name}.jpg"), name) for name in ("cat", "dog", "bird"))


def test_dataset_construction_and_iteration(pairs: tuple[ImageTextPair, ...]) -> None:
    dataset = ImageTextDataset(pairs)

    assert dataset.pairs is pairs
    assert len(dataset) == 3
    assert tuple(dataset) == pairs
    assert list(iter(dataset)) == list(pairs)


@pytest.mark.parametrize("index", [0, 1, 2, -1, -2, -3])
def test_integer_indexing(pairs: tuple[ImageTextPair, ...], index: int) -> None:
    assert ImageTextDataset(pairs)[index] is pairs[index]


@pytest.mark.parametrize("index", [3, -4])
def test_index_out_of_range(pairs: tuple[ImageTextPair, ...], index: int) -> None:
    with pytest.raises(IndexError):
        ImageTextDataset(pairs)[index]


@pytest.mark.parametrize(
    "index",
    [slice(None), slice(1, 3), slice(-2, None), slice(None, None, -1), slice(0, 3, 2), slice(3)],
)
def test_slicing(pairs: tuple[ImageTextPair, ...], index: slice) -> None:
    result = ImageTextDataset(pairs)[index]

    assert isinstance(result, tuple)
    assert result == pairs[index]


@pytest.mark.parametrize("field", ["image_path", "caption", "id"])
def test_pair_fields_are_frozen(field: str) -> None:
    pair = ImageTextPair(Path("cat.jpg"), "A cat")

    with pytest.raises(FrozenInstanceError):
        setattr(pair, field, None)


def test_dataset_field_is_frozen() -> None:
    dataset = ImageTextDataset(())

    with pytest.raises(FrozenInstanceError):
        dataset.pairs = ()


def test_schemas_use_slots() -> None:
    assert not hasattr(ImageTextPair(Path("cat.jpg"), "A cat"), "__dict__")
    assert not hasattr(ImageTextDataset(()), "__dict__")
