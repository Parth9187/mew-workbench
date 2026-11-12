"""Tests for JSONL image-text dataset loading."""

import json
from pathlib import Path

import pytest

from mew.data import ImageTextDataset, ImageTextPair, load_jsonl


def test_multiple_records_and_paths(tmp_path: Path) -> None:
    path = tmp_path / "dataset.jsonl"
    absolute = tmp_path / "absolute.jpg"
    records = [
        {"image_path": "images/cat.jpg", "caption": "A cat", "id": " cat-1 "},
        {"image_path": str(absolute), "caption": ""},
    ]
    path.write_text("\n".join(json.dumps(record) for record in records), encoding="utf-8")

    dataset = load_jsonl(path)

    assert dataset == ImageTextDataset(
        (
            ImageTextPair(tmp_path / "images/cat.jpg", "A cat", " cat-1 "),
            ImageTextPair(absolute, ""),
        )
    )
    assert isinstance(dataset.pairs, tuple)


@pytest.mark.parametrize("id_fields", [{}, {"id": None}, {"id": ""}, {"id": " \t "}])
def test_optional_ids(tmp_path: Path, id_fields: dict[str, str | None]) -> None:
    path = tmp_path / "dataset.jsonl"
    record = {"image_path": "cat.jpg", "caption": "Cat", **id_fields}
    path.write_text(json.dumps(record), encoding="utf-8")

    assert load_jsonl(path)[0].id is None


@pytest.mark.parametrize("encoding", ["utf-8", "utf-8-sig"])
def test_unicode_and_bom(tmp_path: Path, encoding: str) -> None:
    path = tmp_path / "dataset.jsonl"
    path.write_text('{"image_path": "猫.jpg", "caption": "猫 — café"}\n', encoding=encoding)

    assert load_jsonl(path)[0] == ImageTextPair(tmp_path / "猫.jpg", "猫 — café")


@pytest.mark.parametrize("content", ["", "\n \t\n\n", "\ufeff"])
def test_empty_dataset(tmp_path: Path, content: str) -> None:
    path = tmp_path / "dataset.jsonl"
    path.write_text(content, encoding="utf-8")

    assert load_jsonl(path) == ImageTextDataset(())


def test_blank_lines_between_records(tmp_path: Path) -> None:
    path = tmp_path / "dataset.jsonl"
    path.write_text(
        '\n{"image_path":"cat.jpg","caption":"Cat"}\n \t\n'
        '{"image_path":"dog.jpg","caption":"Dog"}\n\n',
        encoding="utf-8",
    )

    assert [pair.caption for pair in load_jsonl(path)] == ["Cat", "Dog"]


@pytest.mark.parametrize("content", ["{", '{"caption":}', "{} {}", '{"caption":"a\nb"}'])
def test_malformed_json(tmp_path: Path, content: str) -> None:
    path = tmp_path / "dataset.jsonl"
    path.write_text(content, encoding="utf-8")

    with pytest.raises(ValueError, match="JSONL line 1: malformed JSON"):
        load_jsonl(path)


@pytest.mark.parametrize("value", [None, [], [1], "text", 42, True])
def test_non_object_values(tmp_path: Path, value: object) -> None:
    path = tmp_path / "dataset.jsonl"
    path.write_text(json.dumps(value), encoding="utf-8")

    with pytest.raises(ValueError, match="JSONL line 1: expected a JSON object"):
        load_jsonl(path)


@pytest.mark.parametrize("field", ["image_path", "caption"])
def test_missing_required_keys(tmp_path: Path, field: str) -> None:
    path = tmp_path / "dataset.jsonl"
    record = {"image_path": "cat.jpg", "caption": "Cat"}
    del record[field]
    path.write_text(json.dumps(record), encoding="utf-8")

    with pytest.raises(ValueError, match=f"JSONL line 1: missing required key '{field}'"):
        load_jsonl(path)


@pytest.mark.parametrize("field", ["image_path", "caption", "id"])
@pytest.mark.parametrize("value", [42, True, [], {}])
def test_incorrect_types(tmp_path: Path, field: str, value: object) -> None:
    path = tmp_path / "dataset.jsonl"
    record: dict[str, object] = {"image_path": "cat.jpg", "caption": "Cat"}
    record[field] = value
    path.write_text(json.dumps(record), encoding="utf-8")

    with pytest.raises(ValueError, match=f"JSONL line 1: '{field}' must be a string"):
        load_jsonl(path)


@pytest.mark.parametrize("field", ["image_path", "caption"])
def test_required_fields_cannot_be_null(tmp_path: Path, field: str) -> None:
    path = tmp_path / "dataset.jsonl"
    record = {"image_path": "cat.jpg", "caption": "Cat", field: None}
    path.write_text(json.dumps(record), encoding="utf-8")

    with pytest.raises(ValueError, match=f"JSONL line 1: '{field}' must be a string"):
        load_jsonl(path)


@pytest.mark.parametrize(
    "invalid", ["{", "[]", '{"caption":"Cat"}', '{"image_path":1,"caption":"Cat"}']
)
def test_error_line_numbers(tmp_path: Path, invalid: str) -> None:
    path = tmp_path / "dataset.jsonl"
    path.write_text(
        '\n{"image_path":"cat.jpg","caption":"Cat"}\n \t\n' + invalid,
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="JSONL line 4:"):
        load_jsonl(path)


def test_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_jsonl(tmp_path / "missing.jsonl")
