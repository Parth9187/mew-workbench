"""Tests for dataset validation and loader integration."""

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from mew.data import (
    ImageTextDataset,
    ImageTextPair,
    ValidationIssue,
    ValidationReport,
    load_csv,
    load_jsonl,
    validate_dataset,
)


@pytest.mark.parametrize(
    "extension", [".jpg", ".jpeg", ".png", ".webp", ".JPG", ".JpEg", ".PNG", ".WEBP"]
)
def test_valid_extensions(tmp_path: Path, extension: str) -> None:
    path = tmp_path / f"image{extension}"
    path.touch()
    dataset = ImageTextDataset((ImageTextPair(path, "Image"), ImageTextPair(path, "Another")))

    report = validate_dataset(dataset)

    assert report == ValidationReport(2, 2, 0, ())
    assert report.is_valid


def test_empty_dataset() -> None:
    report = validate_dataset(ImageTextDataset(()))

    assert report == ValidationReport(0, 0, 0, ())
    assert report.is_valid


@pytest.mark.parametrize("caption", ["", " ", "\t\n", "\u2003"])
def test_blank_captions(tmp_path: Path, caption: str) -> None:
    path = tmp_path / "cat.jpg"
    path.touch()

    report = validate_dataset(ImageTextDataset((ImageTextPair(path, caption),)))

    assert report.issues == (
        ValidationIssue(1, "caption", "empty_caption", "Caption must not be blank."),
    )
    assert (report.total, report.valid, report.invalid) == (1, 0, 1)
    assert not report.is_valid


def test_missing_image(tmp_path: Path) -> None:
    path = tmp_path / "missing.png"

    report = validate_dataset(ImageTextDataset((ImageTextPair(path, "Missing"),)))

    assert [(issue.field, issue.code) for issue in report.issues] == [
        ("image_path", "missing_image")
    ]
    assert str(path) in report.issues[0].message


@pytest.mark.parametrize("name", ["directory.jpg", "directory.gif"])
def test_directory(tmp_path: Path, name: str) -> None:
    path = tmp_path / name
    path.mkdir()

    report = validate_dataset(ImageTextDataset((ImageTextPair(path, "Directory"),)))

    expected = ["not_a_file"]
    if name.endswith(".gif"):
        expected.append("unsupported_extension")
    assert [issue.code for issue in report.issues] == expected
    assert report.invalid == 1


@pytest.mark.parametrize("extension", [".gif", ".txt", ""])
def test_unsupported_extensions(tmp_path: Path, extension: str) -> None:
    path = tmp_path / f"image{extension}"
    path.touch()

    report = validate_dataset(ImageTextDataset((ImageTextPair(path, "Image"),)))

    assert [issue.code for issue in report.issues] == ["unsupported_extension"]
    assert report.issues[0].field == "image_path"


def test_counts_ordering_and_input_immutability(tmp_path: Path) -> None:
    valid = tmp_path / "valid.jpg"
    valid.touch()
    pairs = (
        ImageTextPair(valid, "Valid", "keep-id"),
        ImageTextPair(tmp_path / "missing.gif", " \t"),
        ImageTextPair(tmp_path / "missing.png", "Missing"),
        ImageTextPair(valid, "Also valid"),
    )
    dataset = ImageTextDataset(pairs)

    report = validate_dataset(dataset)

    assert (report.total, report.valid, report.invalid) == (4, 2, 2)
    assert [(issue.record_index, issue.code) for issue in report.issues] == [
        (2, "empty_caption"),
        (2, "missing_image"),
        (2, "unsupported_extension"),
        (3, "missing_image"),
    ]
    assert validate_dataset(dataset) == report
    assert dataset.pairs is pairs
    assert dataset == ImageTextDataset(
        (
            ImageTextPair(valid, "Valid", "keep-id"),
            ImageTextPair(tmp_path / "missing.gif", " \t"),
            ImageTextPair(tmp_path / "missing.png", "Missing"),
            ImageTextPair(valid, "Also valid"),
        )
    )


@pytest.mark.parametrize("format_name", ["csv", "jsonl"])
def test_loaded_datasets(tmp_path: Path, format_name: str) -> None:
    (tmp_path / "valid.jpg").touch()
    path = tmp_path / f"dataset.{format_name}"
    if format_name == "csv":
        path.write_text("image_path,caption\nvalid.jpg,Valid\nmissing.gif,\n", encoding="utf-8")
        dataset = load_csv(path)
    else:
        path.write_text(
            '{"image_path":"valid.jpg","caption":"Valid"}\n'
            '{"image_path":"missing.gif","caption":""}\n',
            encoding="utf-8",
        )
        dataset = load_jsonl(path)

    report = validate_dataset(dataset)

    assert (report.total, report.valid, report.invalid) == (2, 1, 1)
    assert [(issue.record_index, issue.code) for issue in report.issues] == [
        (2, "empty_caption"),
        (2, "missing_image"),
        (2, "unsupported_extension"),
    ]


@pytest.mark.parametrize(
    ("instance", "field"),
    [
        (ValidationIssue(1, "caption", "empty_caption", "Blank"), "message"),
        (ValidationReport(0, 0, 0, ()), "total"),
    ],
)
def test_frozen_slotted_reports(instance: ValidationIssue | ValidationReport, field: str) -> None:
    assert not hasattr(instance, "__dict__")
    with pytest.raises(FrozenInstanceError):
        setattr(instance, field, None)
