"""Tests for CSV image-text dataset loading."""

from pathlib import Path

import pytest

from mew.data import ImageTextDataset, ImageTextPair, load_csv


def test_multiple_rows_and_paths(tmp_path: Path) -> None:
    path = tmp_path / "dataset.csv"
    absolute = tmp_path / "absolute.jpg"
    path.write_text(
        f'image_path,caption,id\nimages/cat.jpg,"A cat, sleeping",cat-1\n{absolute},Dog,dog-2\n',
        encoding="utf-8",
    )

    dataset = load_csv(path)

    assert dataset == ImageTextDataset(
        (
            ImageTextPair(tmp_path / "images/cat.jpg", "A cat, sleeping", "cat-1"),
            ImageTextPair(absolute, "Dog", "dog-2"),
        )
    )
    assert isinstance(dataset.pairs, tuple)


@pytest.mark.parametrize(
    "content",
    [
        "image_path,caption\ncat.jpg,Cat\n",
        "image_path,caption,id\ncat.jpg,Cat,\n",
        "image_path,caption,id\ncat.jpg,Cat,   \n",
        "image_path,caption,id\ncat.jpg,Cat\n",
    ],
)
def test_missing_or_blank_id(tmp_path: Path, content: str) -> None:
    path = tmp_path / "dataset.csv"
    path.write_text(content, encoding="utf-8")

    assert load_csv(path)[0].id is None


@pytest.mark.parametrize(
    ("content", "missing"),
    [
        ("", "image_path, caption"),
        ("caption\nCat\n", "image_path"),
        ("image_path\ncat.jpg\n", "caption"),
        ("image,description\ncat.jpg,Cat\n", "image_path, caption"),
    ],
)
def test_missing_headers(tmp_path: Path, content: str, missing: str) -> None:
    path = tmp_path / "dataset.csv"
    path.write_text(content, encoding="utf-8")

    with pytest.raises(ValueError, match=f"row 1: missing required headers: {missing}"):
        load_csv(path)


@pytest.mark.parametrize(
    ("content", "row", "field"),
    [
        ("image_path,caption\ncat.jpg\n", 2, "caption"),
        ("caption,image_path\nCat,cat.jpg\nDog\n", 3, "image_path"),
    ],
)
def test_incomplete_rows(tmp_path: Path, content: str, row: int, field: str) -> None:
    path = tmp_path / "dataset.csv"
    path.write_text(content, encoding="utf-8")

    with pytest.raises(ValueError, match=f"row {row}: incomplete row; missing fields: {field}"):
        load_csv(path)


@pytest.mark.parametrize("extra", [",unexpected", ",", ",one,two"])
def test_extra_columns(tmp_path: Path, extra: str) -> None:
    path = tmp_path / "dataset.csv"
    path.write_text(f"image_path,caption\ncat.jpg,Cat\ndog.jpg,Dog{extra}\n", encoding="utf-8")

    with pytest.raises(ValueError, match="row 3: extra columns beyond the header"):
        load_csv(path)


def test_header_only(tmp_path: Path) -> None:
    path = tmp_path / "dataset.csv"
    path.write_text("image_path,caption\n", encoding="utf-8")

    assert load_csv(path) == ImageTextDataset(())


@pytest.mark.parametrize("row", [",,", " , \t, ", '"","",""', ","])
def test_null_rows(tmp_path: Path, row: str) -> None:
    path = tmp_path / "dataset.csv"
    path.write_text(f"image_path,caption,id\ncat.jpg,Cat,cat-1\n{row}\n", encoding="utf-8")

    with pytest.raises(ValueError, match="row 3: null row; all fields are empty"):
        load_csv(path)


def test_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_csv(tmp_path / "missing.csv")


def test_utf8_bom(tmp_path: Path) -> None:
    path = tmp_path / "dataset.csv"
    path.write_text("image_path,caption\ncat.jpg,Un chat endormi — 猫\n", encoding="utf-8-sig")

    assert load_csv(path)[0].caption == "Un chat endormi — 猫"


def test_blank_caption_and_nonexistent_image(tmp_path: Path) -> None:
    path = tmp_path / "dataset.csv"
    path.write_text("image_path,caption\nmissing.jpg,\n", encoding="utf-8")

    assert load_csv(path)[0] == ImageTextPair(tmp_path / "missing.jpg", "")
